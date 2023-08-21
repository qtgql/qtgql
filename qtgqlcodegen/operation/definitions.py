from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

import attrs
import graphql
from attr import define

from qtgqlcodegen.utils import HashAbleDict

if TYPE_CHECKING:
    from graphql.language import ast as gql_lang
    from graphql.type import definition as gql_def

    from qtgqlcodegen.schema.definitions import (
        QtGqlArgumentDefinition,
        QtGqlFieldDefinition,
        QtGqlVariableDefinition,
        SchemaTypeInfo,
    )
    from qtgqlcodegen.types import (
        QtGqlObjectType,
        QtGqlQueriedInterface,
        QtGqlQueriedObjectType,
        QtGqlTypeABC,
    )


@attrs.define(slots=False, repr=False)
class OperationTypeInfo:
    schema_type_info: SchemaTypeInfo
    narrowed_types_map: dict[str, QtGqlQueriedObjectType] = attrs.Factory(dict)
    narrowed_interfaces_map: dict[str, QtGqlQueriedInterface] = attrs.Factory(dict)
    variables: list[QtGqlVariableDefinition] = attrs.Factory(list)
    used_fragments: HashAbleDict[str, gql_lang.FragmentDefinitionNode] = attrs.Factory(HashAbleDict)
    available_fragments: HashAbleDict[str, gql_lang.FragmentDefinitionNode] = attrs.Factory(
        HashAbleDict,
    )


@attrs.define(frozen=True, slots=False, repr=False)
class QtGqlQueriedField:
    type: QtGqlTypeABC
    type_info: OperationTypeInfo
    origin: QtGqlObjectType
    concrete: QtGqlFieldDefinition
    variable_uses: list[QtGqlVariableUse] = attrs.Factory(list)

    @cached_property
    def cached_by_args(self) -> bool:
        # if the origin implements node it's fields are cached by arguments
        # if they have ones
        return bool(self.concrete.arguments)

    @cached_property
    def is_root(self) -> bool:
        return self.origin.name in self.type_info.schema_type_info.root_types_names

    @property
    def variable_builder_name(self) -> str:
        return f"build_args_for_{self.name}"

    @property
    def name(self) -> str:
        return self.concrete.name

    @property
    def private_name(self):
        return self.concrete.private_name


@define(slots=False, repr=False)
class QtGqlOperationDefinition:
    operation_def: gql_def.OperationDefinitionNode
    root_type: QtGqlQueriedObjectType
    root_field: QtGqlQueriedField
    variables: list[QtGqlVariableDefinition] = attrs.Factory(list)
    narrowed_types: tuple[QtGqlQueriedObjectType, ...] = attrs.Factory(tuple)
    interfaces: tuple[QtGqlQueriedInterface, ...] = attrs.Factory(tuple)
    used_fragments: tuple[gql_lang.FragmentDefinitionNode, ...] = attrs.Factory(tuple)

    @property
    def generated_variables_type(self) -> str:
        return f"{self.name}Variables"

    @property
    def name(self) -> str:
        assert self.operation_def.name
        return self.operation_def.name.value

    @property
    def query(self) -> str:
        return "\n".join(
            [
                graphql.print_ast(self.operation_def),
                *[graphql.print_ast(frag) for frag in self.used_fragments],
            ],
        )


@define(slots=False, repr=False)
class QtGqlVariableUse:
    argument: tuple[int, QtGqlArgumentDefinition]
    variable: QtGqlVariableDefinition
