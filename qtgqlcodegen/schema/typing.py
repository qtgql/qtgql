from __future__ import annotations

import contextlib
import functools
from abc import abstractmethod, ABC
from functools import cached_property
from typing import TYPE_CHECKING, Callable

import attrs
from attr import define

from qtgqlcodegen.builtin_scalars import BuiltinScalars
from qtgqlcodegen.core.cppref import QtGqlTypes, CppAttribute
from qtgqlcodegen.operation.definitions import QtGqlQueriedObjectType
from qtgqlcodegen.utils import AntiForwardRef, freeze

if TYPE_CHECKING:
    from typing_extensions import TypeVar, Self
    from qtgqlcodegen.schema.definitions import QtGqlInputFieldDefinition, QtGqlFieldDefinition, CustomScalarMap, \
        SchemaTypeInfo


@define
class QtGqlTypeABC(ABC):
    @property
    def is_union(self) -> QtGqlUnion | None:
        return None
    @property
    def is_optional(self) -> bool:
        return False
    @property
    def is_object_type(self) -> QtGqlObjectTypeDefinition | None:
        return None
    @property
    def is_interface(self) -> QtGqlInterfaceDefinition | None:
        return None

    @property
    def is_input_object_type(self) -> QtGqlInputObjectTypeDefinition | None:
        return None

    @property
    def is_model(self) -> QtGqlTypeABC | None:
        return None
    @property
    def is_enum(self) -> QtGqlEnumDefinition | None:
        return None

    @property
    def is_builtin_scalar(self) -> BuiltinScalar | None:
        return None

    @property
    def is_void(self) -> bool:
        if sc := self.is_builtin_scalar:
            return sc is BuiltinScalars.VOID
        return False

    @property
    def is_custom_scalar(self) -> CustomScalarDefinition | None:
        return None

    @property
    @abstractmethod
    def type_name(self) -> str:
        raise NotImplementedError

    @property
    def member_type(self) -> str:
        """
        :returns: Annotation of the field at the concrete type (for the type of the proxy use property type)
        """
        # if the type needs to return something else this is overriden.
        return self.type_name
        # if q_object_def := t_self.is_queried_object_type:
        #     return f"{q_object_def.name}"


@define
class QtGqlOptional(QtGqlTypeABC):
    """
    represents GraphQL types that are not marked with "!"
    """
    of_type: QtGqlTypeABC

    @property
    def is_optional(self) -> bool:
        return True
    @property
    def is_union(self) -> QtGqlUnion | None:
        return self.of_type.is_union

    @property
    def is_object_type(self) -> QtGqlObjectTypeDefinition | None:
        return self.of_type.is_object_type
    @property
    def is_interface(self) -> QtGqlInterfaceDefinition | None:
        return self.of_type.is_interface

    @property
    def is_input_object_type(self) -> QtGqlInputObjectTypeDefinition | None:
        return self.of_type.is_input_object_type

    @property
    def is_model(self) -> QtGqlTypeABC | None:
        return self.of_type.is_model

    @property
    def is_enum(self) -> QtGqlEnumDefinition | None:
        return self.of_type.is_enum

    @property
    def is_builtin_scalar(self) -> BuiltinScalar | None:
        return self.of_type.is_builtin_scalar


    @property
    def member_type(self) -> str:
        return self.of_type.member_type

    @property
    def type_name(self) -> str:
        return self.of_type.type_name


@define
class QtGqlList(QtGqlTypeABC):
    of_type: QtGqlTypeABC
    @property
    def is_model(self) -> QtGqlTypeABC | None:
        # scalars or unions are not supported in lists yet (valid graphql spec though)
        return self.of_type
    @property
    def member_type(self) -> str:
        return f"QMap<QUuid, QList<{self.of_type.member_type}>>"

    @property
    def type_name(self) -> str:
        raise NotImplementedError(
                      "models have no valid type for schema concretes, call member_type",
                  )

@define
class QtGqlUnion(QtGqlTypeABC):
    types: tuple[QtGqlObjectTypeDefinition | QtGqlDeferredType, ...]
    @property
    def is_union(self) -> QtGqlUnion | None:
        return self
    @property
    def type_name(self) -> str:
        raise NotImplementedError

@define
class BuiltinScalar(QtGqlTypeABC):
    attr: CppAttribute
    default_value_: CppAttribute
    graphql_name: str
    from_json_convertor: str

    @property
    def default_value(self) -> str:
        return self.default_value_.name

    @property
    def is_builtin_scalar(self) -> BuiltinScalar | None:
        return self

    @property
    def member_type(self) -> str:
        return self.attr.name

@define
class CustomScalarDefinition(QtGqlTypeABC):
    type_name: str
    graphql_name: str
    deserialized_type: str
    type_for_proxy: str
    include_path: str

    def is_custom_scalar(self) -> CustomScalarDefinition | None:
        return self

@define(slots=False)
class BaseQtGqlObjectType(QtGqlTypeABC):
    name: str
    fields_dict: dict[str, QtGqlFieldDefinition]
    docstring: str | None = ""

    @cached_property
    def fields(self) -> list[QtGqlFieldDefinition]:
        return list(self.fields_dict.values())


@define(slots=False)
class QtGqlObjectTypeDefinition(BaseQtGqlObjectType):
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

    @property
    def is_object_type(self) -> QtGqlObjectTypeDefinition | None:
        return self
    @property
    def type_name(self) -> str:
        return self.name

    @property
    def member_type(self) -> str:
        return f"std::shared_ptr<{self.type_name}>"


    def __attrs_post_init__(self):
        # inject this object type to the interface.
        # later the interface would use this list to know who he might resolve to.
        for base in self.interfaces_raw:
            if not base.implementations.get(self.name):
                base.implementations[self.name] = self

@define
class QtGqlDeferredType(QtGqlTypeABC):
    name: str
    object_map: dict[str, QtGqlObjectTypeDefinition]

    def __getattribute__(self, name):
        resolved = object.__getattribute__(self, 'resolve')()  # alias everything.
        return getattr(resolved, name)

    def resolve(self) -> QtGqlObjectTypeDefinition:
        return self.object_map[self.name]


@define(slots=False, kw_only=True)
class QtGqlInterfaceDefinition(QtGqlObjectTypeDefinition):
    implementations: dict[str, BaseQtGqlObjectType] = attrs.field(factory=dict)

    @cached_property
    def is_node_interface(self) -> bool:
        """As specified by
         https://graphql.org/learn/global-object-identification/#node-interface"""
        if self.name == "Node":
            id_field_maybe = is_builtin_scalar(self.fields[0].type)
            if id_field_maybe and id_field_maybe is BuiltinScalars.ID:
                return True
        return False
    def is_object_type(self) -> QtGqlObjectTypeDefinition | None:
        return None  # although interface extends object this might be confusing.

    @property
    def is_interface(self) -> QtGqlInterfaceDefinition | None:
        return self


@define(slots=False)
class QtGqlInputObjectTypeDefinition(BaseQtGqlObjectType):
    fields_dict: dict[str, QtGqlInputFieldDefinition] = attrs.field(factory=dict)  # type: ignore
    @property
    def is_input_object_type(self) -> QtGqlInputObjectTypeDefinition | None:
        return self

    def type_name(self) -> str:
        return self.name

@define
class EnumValue:
    """encapsulates enumValues from introspection, maps to an Enum member."""

    name: str
    index: int
    description: str = ""


@define(slots=False)
class QtGqlEnumDefinition(QtGqlTypeABC):
    name: str
    members: list[EnumValue]

    @cached_property
    def map_name(self) -> str:
        return f"{self.name}EnumMap"

    @cached_property
    def namespaced_name(self) -> str:
        return f"Enums::{self.name}"

    @property
    def is_enum(self) -> QtGqlEnumDefinition | None:
        return self
    @property
    def type_name(self) -> str:
        return self.namespaced_name
