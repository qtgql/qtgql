from __future__ import annotations

import enum
from functools import cached_property
from typing import TYPE_CHECKING, Generic, TypeVar

import attrs
from attr import Factory
from attrs import define
from typingref import UNSET, TypeHinter

from qtgqlcodegen.builtin_scalars import BuiltinScalars
from qtgqlcodegen.core.cppref import QtGqlTypes

if TYPE_CHECKING:
    from qtgqlcodegen.custom_scalars import CustomScalarDefinition
    from qtgqlcodegen.schema.typing import GqlTypeHinter, SchemaTypeInfo


class Kinds(enum.Enum):
    SCALAR = "SCALAR"
    OBJECT = "OBJECT"
    ENUM = "ENUM"
    LIST = "LIST"
    UNION = "UNION"
    NON_NULL = "NON_NULL"
    INTERFACE = "INTERFACE"
    INPUT_OBJECT = "INPUT_OBJECT"


@define(slots=False)
class QtGqlBaseTypedNode:
    name: str
    type: GqlTypeHinter
    type_info: SchemaTypeInfo

    @cached_property
    def is_custom_scalar(self) -> CustomScalarDefinition | None:
        return self.type.is_custom_scalar


T = TypeVar("T")


@define(slots=False)
class QtGqlVariableDefinition(Generic[T], QtGqlBaseTypedNode):
    default_value: T | None = UNSET

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
        elif self.is_custom_scalar:
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

    @cached_property
    def default_value(self):
        if builtin_scalar := self.type.is_builtin_scalar:
            return builtin_scalar.default_value
        if self.type.is_object_type:
            return "{}"

        if self.type.is_model:
            # this would just generate the model without data.
            return "{}"

        if self.type.is_custom_scalar:
            return "{}"

        if enum_def := self.type.is_enum:
            return f"{enum_def.namespaced_name}(0)"

        raise NotImplementedError

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


@define(slots=False)
class BaseGqlTypeDefinition:
    name: str
    fields_dict: dict[str, QtGqlFieldDefinition]
    docstring: str | None = ""

    @property
    def fields(self) -> list[QtGqlFieldDefinition]:
        return list(self.fields_dict.values())


@define(slots=False, kw_only=True)
class QtGqlObjectTypeDefinition(BaseGqlTypeDefinition):
    interfaces_raw: list[QtGqlInterfaceDefinition] = attrs.Factory(list)

    def implements(self, interface: QtGqlInterfaceDefinition) -> bool:
        for m_interface in self.interfaces_raw:
            if interface is m_interface or m_interface.implements(interface):
                return True
        return False

    @cached_property
    def bases(self) -> list[QtGqlInterfaceDefinition]:
        """
        returns only the top level interfaces that should be inherited.
        if i.e
        ```graphql
        interface Node{
        id: ID!
        }

        interface A implements Node{
        otherField: String!
        }

        type Foo implements A{
        ...
        }
        ```
        Type `Foo` would extend only `A`

        If there are no interfaces returns only NodeInterfaceABC or ObjectTypeABC.
        """
        not_unique_interfaces: list[QtGqlInterfaceDefinition] = []

        if not self.interfaces_raw:
            # TODO(nir): these are not really interfaces though they are inherited if there are no interfaces.
            # https://github.com/qtgql/qtgql/issues/267
            if self.implements_node:
                return [QtGqlTypes.NodeInterfaceABC]  # type: ignore

            else:
                return [QtGqlTypes.ObjectTypeABC]  # type: ignore

        for interface in self.interfaces_raw:
            for other in self.interfaces_raw:
                if other is not interface:
                    if interface.implements(other):
                        not_unique_interfaces.append(other)

        return [intfs for intfs in self.interfaces_raw if intfs not in not_unique_interfaces]

    @cached_property
    def implements_node(self) -> bool:
        if isinstance(self, QtGqlInterfaceDefinition):
            return self.is_node_interface

        return any(base.implements_node for base in self.bases)

    def __attrs_post_init__(self):
        # inject this object type to the interface.
        # later the interface would use this list to know who he might resolve to.
        for base in self.interfaces_raw:
            if not base.implementations.get(self.name):
                base.implementations[self.name] = self


@define(slots=False, kw_only=True)
class QtGqlInterfaceDefinition(QtGqlObjectTypeDefinition):
    implementations: dict[str, BaseGqlTypeDefinition] = attrs.field(factory=dict)

    @cached_property
    def is_node_interface(self) -> bool:
        """As specified by https://graphql.org/learn/global-object-
        identification/#node-interface."""
        if self.name == "Node":
            id_field_maybe = self.fields[0].type.is_builtin_scalar
            if id_field_maybe and id_field_maybe is BuiltinScalars.ID:
                return True
        return False


@define(slots=False)
class QtGqlInputObjectTypeDefinition(BaseGqlTypeDefinition):
    fields_dict: dict[str, QtGqlInputFieldDefinition] = attrs.field(factory=dict)  # type: ignore


@define
class EnumValue:
    """encapsulates enumValues from introspection, maps to an Enum member."""

    name: str
    index: int
    description: str = ""


@define(slots=False)
class QtGqlEnumDefinition:
    name: str
    members: list[EnumValue]

    @cached_property
    def map_name(self) -> str:
        return f"{self.name}EnumMap"

    @cached_property
    def namespaced_name(self) -> str:
        return f"Enums::{self.name}"
