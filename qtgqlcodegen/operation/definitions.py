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

    from qtgqlcodegen.schema.definitions import (
        QtGqlFieldDefinition,
        QtGqlVariableDefinition,
        SchemaTypeInfo,
    )
    from qtgqlcodegen.types import QtGqlQueriedObjectType, QtGqlTypeABC


@attrs.define(slots=False)
class OperationTypeInfo:
    schema_type_info: SchemaTypeInfo
    narrowed_types_map: dict[str, QtGqlQueriedObjectType] = attrs.Factory(dict)
    variables: list[QtGqlVariableDefinition] = attrs.Factory(list)

    def narrowed_types(self) -> tuple[QtGqlQueriedObjectType, ...]:
        return tuple(self.narrowed_types_map.values())


@attrs.define(frozen=True, slots=False, repr=False)
class QtGqlQueriedField:
    concrete: QtGqlFieldDefinition
    type_info: OperationTypeInfo
    choices: frozendict[str, dict[str, QtGqlQueriedField]] = attrs.Factory(frozendict)
    selections: dict[str, QtGqlQueriedField] = attrs.Factory(dict)
    narrowed_type: QtGqlQueriedObjectType | None = None
    is_root: bool = False

    @property
    def type(self) -> QtGqlTypeABC:
        return self.concrete.type

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
        """

        :return: C++ property type that will be exposed to QML.
        """
        tp = self.concrete.type
        if tp.is_object_type:
            assert self.narrowed_type
            return f"{self.type_name} *"

        if cs := tp.is_custom_scalar:
            return cs.to_qt_type

        if model_of := tp.is_model:
            if model_of.is_object_type:
                return f"{self.type_name} *"

        return self.type_name

    @property
    def name(self) -> str:
        return self.concrete.name

    @property
    def private_name(self):
        return self.concrete.private_name

    def as_conf_string(self) -> str:
        return config_template(
            context=ConfigContext(self),
        )


@define(slots=False, repr=False)
class QtGqlOperationDefinition:
    operation_def: gql_def.OperationDefinitionNode
    root_field: QtGqlQueriedField
    fragments: list[str] = attrs.Factory(list)
    variables: list[QtGqlVariableDefinition] = attrs.Factory(list)
    narrowed_types: tuple[QtGqlQueriedObjectType, ...] = attrs.Factory(tuple)

    @property
    def generated_variables_type(self) -> str:
        return self.name + "Variables"

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
