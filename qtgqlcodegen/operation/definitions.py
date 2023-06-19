from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

import attrs
import graphql
from attr import define
from frozendict import frozendict

if TYPE_CHECKING:
    from graphql.type import definition as gql_def

    from qtgqlcodegen.schema.definitions import (
        QtGqlArgumentDefinition,
        QtGqlFieldDefinition,
        QtGqlVariableDefinition,
        SchemaTypeInfo,
    )
    from qtgqlcodegen.types import QtGqlQueriedInterface, QtGqlQueriedObjectType, QtGqlTypeABC


@attrs.define(slots=False)
class OperationTypeInfo:
    schema_type_info: SchemaTypeInfo
    narrowed_types_map: dict[str, QtGqlQueriedObjectType] = attrs.Factory(dict)
    narrowed_interfaces_map: dict[str, QtGqlQueriedInterface] = attrs.Factory(dict)
    variables: list[QtGqlVariableDefinition] = attrs.Factory(list)


@attrs.define(frozen=True, slots=False, repr=False)
class QtGqlQueriedField:
    type: QtGqlTypeABC
    concrete: QtGqlFieldDefinition
    choices: frozendict[str, dict[str, QtGqlQueriedField]] = attrs.Factory(frozendict)
    selections: dict[str, QtGqlQueriedField] = attrs.Factory(dict)
    variable_uses: list[QtGqlVariableUse, ...] = attrs.Factory(list)
    is_root: bool = False

    @cached_property
    def type_name(self) -> str:
        if self.type.is_object_type:
            return self.type.type_name()

        if model_of := self.type.is_model:
            if model_of.is_object_type:
                return f"qtgql::bases::ListModelABC<{self.type.type_name()}>"

        return self.type.member_type

    @cached_property
    def property_type(self) -> str:
        """

        :return: C++ property type that will be exposed to QML.
        """
        tp = self.concrete.type
        if tp.is_object_type:
            return f"{self.type_name} *"

        if cs := tp.is_custom_scalar:
            return cs.to_qt_type

        if model_of := tp.is_model:
            if model_of.is_object_type:
                return f"{self.type_name} *"

        return f"{self.type_name} &"

    @cached_property
    def build_variables_tuple_for_field_arguments(self) -> str:
        if self.concrete.arguments:
            return (
                "{"
                + ",".join(
                    [
                        f"operation->vars_inst.{arg.variable.name}.value()"
                        for arg in self.variable_uses
                    ],
                )
                + "}"
            )
        return ""

    @property
    def name(self) -> str:
        return self.concrete.name

    @property
    def private_name(self):
        return self.concrete.private_name


@define(slots=False, repr=False)
class QtGqlOperationDefinition:
    operation_def: gql_def.OperationDefinitionNode
    root_field: QtGqlQueriedField
    fragments: list[str] = attrs.Factory(list)
    variables: list[QtGqlVariableDefinition] = attrs.Factory(list)
    narrowed_types: tuple[QtGqlQueriedObjectType, ...] = attrs.Factory(tuple)
    interfaces: tuple[QtGqlQueriedInterface, ...] = attrs.Factory(tuple)

    @property
    def generated_variables_type(self) -> str:
        return self.name + "Variables"

    @property
    def name(self) -> str:
        assert self.operation_def.name
        return self.operation_def.name.value

    @property
    def query(self) -> str:
        return graphql.print_ast(self.operation_def)


@define(slots=False, repr=False)
class QtGqlVariableUse:
    argument: tuple[int, QtGqlArgumentDefinition]
    variable: QtGqlVariableDefinition
