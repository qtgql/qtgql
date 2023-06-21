from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Literal

from attr import Factory, define
from graphql import OperationType

if TYPE_CHECKING:
    from graphql.type import definition as gql_def
    from typing_extensions import TypeAlias

    from qtgqlcodegen.types import (
        CustomScalarDefinition,
        QtGqlEnumDefinition,
        QtGqlInputObjectTypeDefinition,
        QtGqlInterface,
        QtGqlObjectType,
        QtGqlTypeABC,
    )


@define(slots=False)
class QtGqlBaseTypedNode:
    name: str
    type: QtGqlTypeABC

    @cached_property
    def is_custom_scalar(self) -> CustomScalarDefinition | None:
        return self.type.is_custom_scalar


@define(slots=False)
class QtGqlVariableDefinition(QtGqlBaseTypedNode):
    def json_repr(self, attr_name: str | None = None) -> str:
        if not attr_name:
            attr_name = self.name
        attr_name += ".value()"  # unwrap optional
        return self.type.json_repr(attr_name)


@define(slots=False)
class BaseQtGqlFieldDefinition(QtGqlBaseTypedNode):
    description: str | None = ""


@define(slots=False)
class QtGqlArgumentDefinition(BaseQtGqlFieldDefinition, QtGqlVariableDefinition):
    ...


@define(slots=False, kw_only=True)
class QtGqlFieldDefinition(BaseQtGqlFieldDefinition):
    arguments_dict: dict[str, QtGqlArgumentDefinition] = Factory(dict)

    @cached_property
    def arguments(self) -> tuple[QtGqlArgumentDefinition, ...]:
        return tuple(self.arguments_dict.values())

    @cached_property
    def arguments_type(self) -> str:
        return "std::tuple<" + ",".join([arg.type.type_name() for arg in self.arguments]) + ">"

    def index_for_argument(self, arg: str) -> int:
        return self.arguments.index(self.arguments_dict[arg])

    @cached_property
    def getter_name(self) -> str:
        return f"get_{self.name}"

    @cached_property
    def setter_name(self) -> str:
        return f"set_{self.name}"

    @cached_property
    def signal_name(self) -> str:
        return f"{self.name}Changed"

    @cached_property
    def private_name(self) -> str:
        return f"m_{self.name}"

    @cached_property
    def implements_node(self) -> bool:
        """Helper to check whether the field type implements node."""
        object_type = self.type.is_object_type or self.type.is_interface
        if not object_type:
            if self.type.is_model:
                object_type = self.type.is_model.of_type.is_object_type
        if object_type:
            return object_type.implements_node
        return False


EnumMap: TypeAlias = "dict[str, QtGqlEnumDefinition]"
ObjectTypeMap: TypeAlias = "dict[str, QtGqlObjectType]"
InputObjectMap: TypeAlias = "dict[str, QtGqlInputObjectTypeDefinition]"
InterfacesMap: TypeAlias = "dict[str, QtGqlInterface]"
CustomScalarMap: TypeAlias = "dict[str, CustomScalarDefinition]"


@define(slots=False)
class SchemaTypeInfo:
    schema_definition: gql_def.GraphQLSchema
    custom_scalars: CustomScalarMap
    operation_types: dict[
        Literal["query", "mutation", "subscription"],
        QtGqlObjectType,
    ] = Factory(dict)
    object_types: ObjectTypeMap = Factory(dict)
    enums: EnumMap = Factory(dict)
    input_objects: InputObjectMap = Factory(dict)
    interfaces: InterfacesMap = Factory(dict)

    def get_interface(self, name: str) -> QtGqlInterface | None:
        return self.interfaces.get(name, None)

    def get_object_type(self, name: str) -> QtGqlObjectType | None:
        return self.object_types.get(name, None)

    def add_objecttype(self, objecttype: QtGqlObjectType) -> None:
        self.object_types[objecttype.name] = objecttype

    @cached_property
    def root_types(self) -> list[gql_def.GraphQLObjectType | None]:
        return [
            self.schema_definition.get_root_type(OperationType.QUERY),
            self.schema_definition.get_root_type(OperationType.MUTATION),
            self.schema_definition.get_root_type(OperationType.SUBSCRIPTION),
        ]

    @cached_property
    def root_types_names(self) -> str:
        return " ".join([tp.name for tp in self.root_types if tp])
