from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cached_property
from typing import TYPE_CHECKING

import attrs
from attr import define

from qtgqlcodegen.core.cppref import CppAttribute, QtGqlBasesNs, QtGqlTypes

if TYPE_CHECKING:
    from qtgqlcodegen.operation.definitions import QtGqlQueriedField
    from qtgqlcodegen.schema.definitions import (
        CustomScalarMap,
        QtGqlFieldDefinition,
        QtGqlInputFieldDefinition,
    )


@define
class QtGqlTypeABC(ABC):
    @property
    def is_union(self) -> QtGqlUnion | None:
        return None

    @property
    def is_optional(self) -> bool:
        return False

    @property
    def is_object_type(self) -> QtGqlObjectType | None:
        return None

    @property
    def is_queried_object_type(self) -> QtGqlQueriedObjectType | None:
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

    def json_repr(self, attr_name: str | None = None) -> str:
        raise NotImplementedError(f"{self} is not supported as an input type ATM")

    @property
    def is_custom_scalar(self) -> CustomScalarDefinition | None:
        return None

    @property
    @abstractmethod
    def type_name(self) -> str:
        """
        :returns: The C++ "real" type mostly this would be the member type as well.
        """
        raise NotImplementedError

    @property
    def default_value(self) -> str:
        """

        :return: C++ default value initializer for this type
        """
        return "{}"

    @property
    def member_type(self) -> str:
        """
        :returns: The C++ type of the concrete member
        """
        # if the type needs to return something else this is overridden.
        return self.type_name

    def __str__(self):
        raise RuntimeError("the template probobly tried to render this object")


@define
class QtGqlOptional(QtGqlTypeABC):
    """Represents GraphQL types that are not marked with "!"."""

    of_type: QtGqlTypeABC

    def __getattr__(self, item):
        if item == "is_optional":
            return True
        return getattr(self.of_type, item)

    def __getattribute__(self, name):
        if name not in ("of_type"):
            raise AttributeError
        else:
            return super().__getattribute__(name)

    @property
    def type_name(self) -> str:  # pragma: no cover
        raise NotImplementedError


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
    types: tuple[QtGqlObjectType | QtGqlDeferredType, ...]

    @property
    def is_union(self) -> QtGqlUnion | None:
        return self

    @property
    def type_name(self) -> str:
        raise NotImplementedError

    @property
    def default_value(self) -> str:
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
    def type_name(self) -> str:
        return self.attr.name

    @property
    def is_void(self) -> bool:
        return self is BuiltinScalars.VOID

    def json_repr(self, attr_name: str | None = None) -> str:
        return f"{attr_name}"


@define
class CustomScalarDefinition(QtGqlTypeABC):
    type_name: str
    graphql_name: str
    deserialized_type: str
    type_for_proxy: str
    include_path: str

    @property
    def is_custom_scalar(self) -> CustomScalarDefinition | None:
        return self

    def json_repr(self, attr_name: str | None = None) -> str:
        return f"{attr_name}.serialize()"


@define(slots=False)
class BaseQtGqlObjectType(QtGqlTypeABC):
    name: str
    fields_dict: dict[str, QtGqlFieldDefinition]
    docstring: str | None = ""

    @cached_property
    def fields(self) -> list[QtGqlFieldDefinition]:
        return list(self.fields_dict.values())


@define(slots=False)
class QtGqlObjectType(BaseQtGqlObjectType):
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
    def is_object_type(self) -> QtGqlObjectType | None:
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


@define(slots=False, repr=False)
class QtGqlQueriedObjectType(QtGqlTypeABC):
    concrete: QtGqlObjectType = attrs.field(on_setattr=attrs.setters.frozen)
    fields_dict: dict[str, QtGqlQueriedField] = attrs.Factory(dict)
    is_root_field: bool = False

    @property
    def is_queried_object_type(self) -> QtGqlQueriedObjectType | None:
        return self

    @cached_property
    def fields(self) -> tuple[QtGqlQueriedField, ...]:
        return tuple(self.fields_dict.values())

    @cached_property
    def name(self) -> str:
        return f"{self.concrete.name}__{'$'.join(sorted(self.fields_dict.keys()))}"

    @cached_property
    def doc_fields(self) -> str:
        return "{} {{\n  {}\n}}".format(
            self.concrete.name,
            "\n   ".join(self.fields_dict.keys()),
        )

    @property
    def type_name(self) -> str:
        return self.name

    @cached_property
    def references(self) -> list[QtGqlQueriedField]:
        return [f for f in self.fields if f.type.is_object_type]

    @cached_property
    def models(self) -> list[QtGqlQueriedField]:
        return [f for f in self.fields if f.type.is_model]

    @cached_property
    def private_name(self) -> str:
        return f"m_{self.name}"


@define
class QtGqlDeferredType(QtGqlTypeABC):
    name: str
    object_map__: dict[str, QtGqlObjectType]
    cached_: QtGqlTypeABC | None = None

    def __getattr__(self, item):
        if not self.cached_:
            self.cached_ = self.object_map__[self.name]  # alias everything.
        return getattr(self.cached_, item)

    def __getattribute__(self, name):
        if name not in ("resolve", "object_map__", "cached_", "name"):
            raise AttributeError
        else:
            return super().__getattribute__(name)

    @property
    def type_name(self) -> str:  # we only override it since it is abstractmethod
        raise NotImplementedError("this should not be reached since we override __getattribute__")


@define(slots=False, kw_only=True)
class QtGqlInterfaceDefinition(QtGqlObjectType):
    implementations: dict[str, BaseQtGqlObjectType] = attrs.field(factory=dict)

    @cached_property
    def is_node_interface(self) -> bool:
        """As specified by https://graphql.org/learn/global-object-
        identification/#node-interface."""
        if self.name == "Node":
            id_field_maybe = self.fields[0]
            return (
                id_field_maybe.name == "id"
                and id_field_maybe.type.is_builtin_scalar is BuiltinScalars.ID
            )
        return False

    @property
    def is_object_type(self) -> QtGqlObjectType | None:
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

    @property
    def type_name(self) -> str:
        return self.name

    def json_repr(self, attr_name: str | None = None) -> str:
        return f"{attr_name}.to_json()"


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

    @property
    def default_value(self) -> str:
        return f"{self.namespaced_name}(0)"

    def json_repr(self, attr_name: str | None = None) -> str:
        return f"Enums::{self.map_name}::name_by_value({attr_name})"


def ScalarsNs() -> CppAttribute:
    return QtGqlBasesNs().ns_add("scalars")


def DefaultsNs() -> CppAttribute:
    return QtGqlBasesNs().ns_add("DEFAULTS")


class _BuiltinScalars:
    INT = BuiltinScalar(
        CppAttribute("int"),
        DefaultsNs().ns_add("INT"),
        graphql_name="Int",
        from_json_convertor="toInt()",
    )
    FLOAT = BuiltinScalar(
        CppAttribute("float"),
        DefaultsNs().ns_add("FLOAT"),
        graphql_name="Float",
        from_json_convertor="toDouble()",
    )
    STRING = BuiltinScalar(
        CppAttribute("QString"),
        DefaultsNs().ns_add("STRING"),
        graphql_name="String",
        from_json_convertor="toString()",
    )
    ID = BuiltinScalar(
        ScalarsNs().ns_add("Id"),
        DefaultsNs().ns_add("ID"),
        graphql_name="ID",
        from_json_convertor="toString()",
    )
    BOOLEAN = BuiltinScalar(
        CppAttribute("bool"),
        DefaultsNs().ns_add("BOOL"),
        graphql_name="Boolean",
        from_json_convertor="toBool()",
    )
    VOID = BuiltinScalar(
        ScalarsNs().ns_add("Void"),
        DefaultsNs().ns_add("VOID"),
        graphql_name="Void",
        from_json_convertor="",
    )

    UUID = BuiltinScalar(
        CppAttribute("QUuid"),
        DefaultsNs().ns_add("UUID"),
        graphql_name="UUID",
        from_json_convertor="toVariant().toUuid()",
    )

    @classmethod
    def __iter__(cls):
        for name, member in cls.__dict__.items():
            if name.isupper():
                yield member

    def by_graphql_name(self, name: str) -> BuiltinScalar | None:
        for scalar in self:
            if scalar.graphql_name == name:
                return scalar

    @cached_property
    def keys(self) -> list[str]:
        return [scalar.graphql_name for scalar in self]


BuiltinScalars = _BuiltinScalars()
DateTimeScalarDefinition = CustomScalarDefinition(
    type_name="qtgql::customscalars::DateTimeScalar",
    graphql_name="DateTime",
    deserialized_type="QDateTime",
    type_for_proxy="QString",
    include_path="<qtgql/customscalars/customscalars.hpp>",
)
DateScalarDefinition = CustomScalarDefinition(
    type_name="qtgql::customscalars::DateScalar",
    graphql_name="Date",
    deserialized_type="QDate",
    type_for_proxy="QString",
    include_path="<qtgql/customscalars/customscalars.hpp>",
)
TimeScalarDefinition = CustomScalarDefinition(
    type_name="qtgql::customscalars::TimeScalar",
    graphql_name="Time",
    deserialized_type="QTime",
    type_for_proxy="QString",
    include_path="<qtgql/customscalars/customscalars.hpp>",
)
DecimalScalarDefinition = CustomScalarDefinition(
    type_name="qtgql::customscalars::DecimalScalar",
    graphql_name="Decimal",
    deserialized_type="QString",
    type_for_proxy="QString",
    include_path="<qtgql/customscalars/customscalars.hpp>",
)
CUSTOM_SCALARS: CustomScalarMap = {
    DateTimeScalarDefinition.graphql_name: DateTimeScalarDefinition,
    DateScalarDefinition.graphql_name: DateScalarDefinition,
    TimeScalarDefinition.graphql_name: TimeScalarDefinition,
    DecimalScalarDefinition.graphql_name: DecimalScalarDefinition,
}
