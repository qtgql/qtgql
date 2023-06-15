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
        QtGqlInterfaceDefinition,
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
class QtGqlInputFieldDefinition(BaseQtGqlFieldDefinition, QtGqlVariableDefinition):
    ...


@define(slots=False)
class QtGqlArgumentDefinition(QtGqlInputFieldDefinition):
    ...


@define(slots=False, kw_only=True)
class QtGqlFieldDefinition(BaseQtGqlFieldDefinition):
    arguments: list[QtGqlInputFieldDefinition] = Factory(list)

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
    def can_select_id(self) -> QtGqlFieldDefinition | None:
        """
        :return: The id field of this field object/model type if implements `Node`
        """
        object_type = self.type.is_object_type or self.type.is_interface
        if not object_type:
            if self.type.is_model:
                object_type = self.type.is_model.is_object_type
        if object_type and object_type.implements_node:
            return object_type.fields_dict["id"]


EnumMap: TypeAlias = "dict[str, QtGqlEnumDefinition]"
ObjectTypeMap: TypeAlias = "dict[str, QtGqlObjectType]"
InputObjectMap: TypeAlias = "dict[str, QtGqlInputObjectTypeDefinition]"
InterfacesMap: TypeAlias = "dict[str, QtGqlInterfaceDefinition]"
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

    def get_interface(self, name: str) -> QtGqlInterfaceDefinition | None:
        return self.interfaces.get(name, None)

    def get_object_type(self, name: str) -> QtGqlObjectType | None:
        return self.object_types.get(name, None)

    def set_objecttype(self, objecttype: QtGqlObjectType) -> None:
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
