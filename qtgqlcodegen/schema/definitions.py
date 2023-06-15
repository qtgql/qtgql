from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Literal

from attr import Factory, define
from graphql import OperationType
from typingref import TypeHinter

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
        if self.type.is_input_object_type:
            return f"{attr_name}.to_json()"
        elif self.type.is_builtin_scalar:
            return f"{attr_name}"
        elif enum_def := self.type.is_enum:
            return f"Enums::{enum_def.map_name}::name_by_value({attr_name})"
        elif self.type.is_custom_scalar:
            return f"{attr_name}.serialize()"

        raise NotImplementedError(f"{self.type} is not supported as an input type ATM")


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

    @property
    def default_value(self):
        return self.type.default_value()

    @cached_property
    def member_type(self) -> str:
        """
        :returns: Annotation of the field based on the real type,
        meaning that the private attribute would be of that type.
        this goes for init and the property setter.
        """

        ret = self.type.member_type
        # if self.arguments:
        return ret

    @cached_property
    def fget_annotation(self) -> str:
        """This annotates the value that is QML-compatible."""
        if custom_scalar := self.type.is_custom_scalar:
            return TypeHinter.from_annotations(
                custom_scalar.type_for_proxy,
            ).stringify()
        if self.type.is_enum:
            return "int"

        return self.member_type

    @cached_property
    def type_for_proxy(self) -> str:
        if self.type.is_builtin_scalar or self.type.is_custom_scalar:
            return self.fget_annotation
        else:
            if self.type.is_enum:
                # QEnum value must be int
                return "int"
            # might be a model, which is also QObject
            # graphql doesn't support scalars or enums in Unions ATM.
            assert (
                self.type.is_model
                or self.type.is_object_type
                or self.type.is_interface
                or self.type.is_union
            )
            return "QObject"

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
