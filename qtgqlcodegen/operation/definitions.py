from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

import attrs
import graphql
from attr import define
from frozendict import frozendict

from qtgqlcodegen.operation.template import ConfigContext, config_template

if TYPE_CHECKING:
    from graphql.type import definition as gql_def

    from qtgqlcodegen.operation.typing import OperationTypeInfo
    from qtgqlcodegen.schema.typing import GqlTypeHinter, SchemaTypeInfo, QtGqlVariableDefinition, QtGqlFieldDefinition, \
    QtGqlObjectTypeDefinition


@attrs.define(frozen=True, slots=False, repr=False)
class QtGqlQueriedField:
    definition: QtGqlFieldDefinition
    type_info: OperationTypeInfo
    choices: frozendict[str, dict[str, QtGqlQueriedField]] = attrs.Factory(frozendict)
    selections: dict[str, QtGqlQueriedField] = attrs.Factory(dict)
    narrowed_type: QtGqlQueriedObjectType | None = None
    is_root: bool = False

    @cached_property
    def type(self) -> GqlTypeHinter:
        return self.definition.type

    @cached_property
    def type_name(self) -> str:
        if self.type.is_object_type:
            assert self.narrowed_type
            return self.narrowed_type.name

        if model_of := self.type.is_model:
            if model_of.is_object_type:
                assert self.narrowed_type
                return f"qtgql::bases::ListModelABC<{self.narrowed_type.name}>"

        return self.type.member_type

    @cached_property
    def property_type(self) -> str:
        tp = self.definition.type
        if tp.is_object_type:
            assert self.narrowed_type
            return f"{self.type_name} *"

        if cs := tp.is_custom_scalar:
            return cs.type_for_proxy

        if model_of := tp.is_model:
            if model_of.is_object_type:
                return f"{self.type_name} *"

        return self.type_name

    @cached_property
    def name(self) -> str:
        if self.is_root:
            return "data"
        return self.definition.name

    @cached_property
    def private_name(self):
        if self.is_root:
            return f"m_{self.name}"
        return self.definition.private_name

    def as_conf_string(self) -> str:
        return config_template(
            context=ConfigContext(self),
        )


@define(slots=False, repr=False)
class QtGqlQueriedObjectType:
    definition: QtGqlObjectTypeDefinition = attrs.field(on_setattr=attrs.setters.frozen)
    fields_dict: dict[str, QtGqlQueriedField] = attrs.Factory(dict)
    is_root_field: bool = False

    @cached_property
    def fields(self) -> tuple[QtGqlQueriedField, ...]:
        return tuple(self.fields_dict.values())

    @cached_property
    def name(self) -> str:
        return f"{self.definition.name}__{'$'.join(sorted(self.fields_dict.keys()))}"

    @cached_property
    def doc_fields(self) -> str:
        return "{} {{\n  {}\n}}".format(
            self.definition.name,
            "\n   ".join(self.fields_dict.keys()),
        )

    @cached_property
    def references(self) -> list[QtGqlQueriedField]:
        return [f for f in self.fields if f.type.is_object_type]

    @cached_property
    def models(self) -> list[QtGqlQueriedField]:
        return [f for f in self.fields if f.type.is_model]

    @cached_property
    def private_name(self) -> str:
        return f"m_{self.name}"


@define(slots=False, repr=False)
class QtGqlOperationDefinition:
    operation_def: gql_def.OperationDefinitionNode
    root_field: QtGqlQueriedField
    fragments: list[str] = attrs.Factory(list)
    variables: list[QtGqlVariableDefinition] = attrs.Factory(list)
    narrowed_types_map: dict[str, QtGqlQueriedObjectType] = attrs.Factory(dict)

    @property
    def operation_config(self) -> str:
        return self.root_field.as_conf_string()

    @property
    def name(self) -> str:
        assert self.operation_def.name
        return self.operation_def.name.value

    @cached_property
    def query(self) -> str:
        return graphql.print_ast(self.operation_def)
