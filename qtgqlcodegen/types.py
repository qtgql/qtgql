from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from functools import cached_property
from typing import TYPE_CHECKING, cast

import attrs
from attr import define

from qtgqlcodegen.core.cppref import CppAttribute, QtGqlBasesNs, QtGqlTypes

if TYPE_CHECKING:
    from qtgqlcodegen.operation.definitions import QtGqlQueriedField
    from qtgqlcodegen.schema.definitions import (
        CustomScalarMap,
        QtGqlArgumentDefinition,
        QtGqlFieldDefinition,
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
    def is_interface(self) -> QtGqlInterface | None:
        return None

    @property
    def is_input_object_type(self) -> QtGqlInputObjectTypeDefinition | None:
        return None

    @property
    def is_model(self) -> QtGqlList | None:
        return None

    @property
    def is_enum(self) -> QtGqlEnumDefinition | None:
        return None

    @property
    def is_builtin_scalar(self) -> BuiltinScalar | None:
        return None

    @property
    def is_custom_scalar(self) -> CustomScalarDefinition | None:
        return None

    @property
    def is_queried_object_type(self) -> QtGqlQueriedObjectType | None:
        return None

    @property
    def is_queried_interface(self) -> QtGqlQueriedInterface | None:
        return None

    @property
    def is_queried_union(self) -> QtGqlQueriedUnion | None:
        return None

    def json_repr(self, attr_name: str | None = None) -> str:
        raise NotImplementedError(f"{self} is not supported as an input type ATM")

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
        :returns: The C++ type of the concrete instance member.
        """
        # Usually `type_name` should suffice, if the type needs to return something else this is overridden.
        return self.type_name()

    @property
    def member_type_arg(self) -> str:
        """

        :return: The C++ member_type if it was passed in argument to somewhere.
        """
        return self.member_type

    @property
    def fget_type(self) -> str:
        """

        :return: type for the proxy object, usually this would be the member type though for custom scalars
        there is `to_qt` that has different type.
        """
        return self.member_type

    @property
    def getter_is_constable(self) -> bool:
        return True

    def __str__(self) -> str:  # pragma: no cover
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

    def type_name(self) -> str:  # pragma: no cover
        raise NotImplementedError


@define
class QtGqlList(QtGqlTypeABC):
    of_type: QtGqlTypeABC

    @property
    def is_model(self) -> QtGqlList | None:
        return self

    @property
    def member_type(self) -> str:
        return f"QList<{self.of_type.member_type}>"

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

    def type_name(self) -> str:
        raise NotImplementedError

    @property
    def default_value(self) -> str:
        raise NotImplementedError

    def get_by_name(self, name: str) -> QtGqlObjectType | None:
        for possible in self.types:
            if possible.name == name:
                return cast(QtGqlObjectType, possible)


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

    def type_name(self) -> str:
        return self.attr.name

    @property
    def is_void(self) -> bool:
        return self is BuiltinScalars.VOID

    def json_repr(self, attr_name: str | None = None) -> str:
        return f"{attr_name}"


@define
class CustomScalarDefinition(QtGqlTypeABC):
    name: str
    graphql_name: str
    deserialized_type: str
    to_qt_type: str
    include_path: str

    @property
    def is_custom_scalar(self) -> CustomScalarDefinition | None:
        return self

    def json_repr(self, attr_name: str | None = None) -> str:
        return f"{attr_name}.serialize()"

    def type_name(self) -> str:
        return self.name

    @property
    def fget_type(self) -> str:
        return self.to_qt_type

    @property
    def getter_is_constable(self) -> bool:
        return False


@define(slots=False)
class BaseQtGqlObjectType(QtGqlTypeABC):
    name: str
    fields_dict: dict[str, QtGqlFieldDefinition]
    docstring: str | None = ""

    @cached_property
    def fields(self) -> tuple[QtGqlFieldDefinition, ...]:
        return tuple(self.fields_dict.values())


@define(slots=False)
class QtGqlObjectType(BaseQtGqlObjectType):
    interfaces_raw: tuple[QtGqlInterface, ...] = attrs.Factory(tuple)
    unique_fields: tuple[QtGqlFieldDefinition, ...] = attrs.Factory(tuple)
    is_root: bool = False

    def implements(self, interface: QtGqlInterface) -> bool:
        for m_interface in self.interfaces_raw:
            if interface is m_interface or m_interface.implements(interface):
                return True
        return False

    @cached_property
    def bases(self) -> list[QtGqlInterface]:
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
        not_unique_interfaces: list[QtGqlInterface] = []

        if not self.interfaces_raw:
            # TODO(https://github.com/qtgql/qtgql/issues/267): these are not really interfaces though they are inherited if there are no interfaces.
            if interface := self.is_interface:
                if interface.is_node_interface:
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
        return any(interface.is_node_interface for interface in self.interfaces_raw)

    @property
    def is_object_type(self) -> QtGqlObjectType | None:
        return self

    def type_name(self) -> str:
        return self.name

    @property
    def member_type(self) -> str:
        if self.is_root:
            return self.type_name()  # root types are singletons
        return f"std::shared_ptr<{self.type_name()}>"

    @property
    def member_type_arg(self) -> str:
        pointer_type = "*" if self.is_root else "&"
        return f"{self.member_type} {pointer_type}"

    def __attrs_post_init__(self):
        # inject this object type to the interface.
        # later the interface would use this list to know who he might resolve to.
        for base in self.interfaces_raw:
            if not base.implementations.get(self.name):
                base.implementations[self.name] = self


@define
class QtGqlDeferredType(QtGqlTypeABC):
    name: str
    object_map__: dict[str, QtGqlObjectType]
    cached_: QtGqlTypeABC | None = None

    def __getattr__(self, item):
        if not self.cached_:
            self.cached_ = self.object_map__[self.name]
        try:
            return getattr(self.cached_, item)
        except AttributeError:  # pragma: no cover
            raise Exception(f"{self.cached_.__class__} has no attribute named {item}")

    def __getattribute__(self, name):
        if name not in ("resolve", "object_map__", "cached_", "name"):
            raise AttributeError
        else:
            return super().__getattribute__(name)

    def type_name(self) -> str:  # we only override it since it is abstractmethod
        raise NotImplementedError("this should not be reached since we override __getattribute__")


@define(slots=False, kw_only=True)
class QtGqlInterface(QtGqlObjectType):
    implementations: dict[str, BaseQtGqlObjectType] = attrs.field(factory=dict)

    @cached_property
    def is_node_interface(self) -> bool:
        """As specified by https://graphql.org/learn/global-object-
        identification/#node-interface."""
        if self.name == "Node":
            id_field_maybe = self.fields[0]
            return id_field_maybe.name == "id" and id_field_maybe.type is BuiltinScalars.ID
        return False

    @property
    def is_object_type(self) -> QtGqlObjectType | None:
        return None  # although interface extends object this might be confusing.

    @property
    def is_interface(self) -> QtGqlInterface | None:
        return self


@define(slots=False)
class QtGqlInputObjectTypeDefinition(BaseQtGqlObjectType):
    fields_dict: dict[str, QtGqlArgumentDefinition] = attrs.field(factory=dict)  # type: ignore

    @property
    def is_input_object_type(self) -> QtGqlInputObjectTypeDefinition | None:
        return self

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

    def type_name(self) -> str:
        return self.namespaced_name

    @property
    def default_value(self) -> str:
        return f"{self.namespaced_name}(0)"

    def json_repr(self, attr_name: str | None = None) -> str:
        return f"Enums::{self.map_name}::name_by_value({attr_name})"


@define
class QtGqlQueriedTypeABC:
    concrete: QtGqlTypeABC


@define(slots=False, repr=False)
class QtGqlQueriedObjectType(QtGqlQueriedTypeABC, QtGqlTypeABC):
    name: str
    concrete: QtGqlObjectType
    fields_dict: dict[str, QtGqlQueriedField] = attrs.Factory(dict)

    @property
    def is_queried_object_type(self) -> QtGqlQueriedObjectType | None:
        return self

    @cached_property
    def fields(self) -> tuple[QtGqlQueriedField, ...]:
        return tuple(self.fields_dict.values())

    @property
    def deserializer_name(self) -> str:
        return f"deserializers::des_{self.name}"

    @property
    def updater_name(self) -> str:
        return f"updaters::update_{self.name}"

    def type_name(self) -> str:
        return self.name

    @cached_property
    def references(self) -> list[QtGqlQueriedField]:
        return [f for f in self.fields if f.type.is_queried_object_type]

    @cached_property
    def models(self) -> list[QtGqlQueriedField]:
        return [f for f in self.fields if f.type.is_model]

    @cached_property
    def private_name(self) -> str:
        return f"m_{self.name}"


@define(slots=False, repr=False)
class QtGqlQueriedInterface(QtGqlQueriedObjectType):
    choices: defaultdict[str, dict[str, QtGqlQueriedField]] = attrs.Factory(
        lambda: defaultdict(dict),
    )

    @property
    def is_queried_object_type(self) -> QtGqlQueriedObjectType | None:
        return None

    @property
    def is_queried_interface(self) -> QtGqlQueriedInterface | None:
        return self


@define(slots=False, repr=False)
class QtGqlQueriedUnion(QtGqlQueriedTypeABC, QtGqlTypeABC):
    concrete: QtGqlUnion
    choices: defaultdict[str, dict[str, QtGqlQueriedField]] = attrs.Factory(
        lambda: defaultdict(dict),
    )

    @property
    def is_queried_union(self) -> QtGqlQueriedUnion | None:
        return self

    def type_name(self) -> str:
        return self.concrete.type_name()


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
    name="qtgql::customscalars::DateTimeScalar",
    graphql_name="DateTime",
    deserialized_type="QDateTime",
    to_qt_type="QString",
    include_path="<qtgql/customscalars/customscalars.hpp>",
)
DateScalarDefinition = CustomScalarDefinition(
    name="qtgql::customscalars::DateScalar",
    graphql_name="Date",
    deserialized_type="QDate",
    to_qt_type="QString",
    include_path="<qtgql/customscalars/customscalars.hpp>",
)
TimeScalarDefinition = CustomScalarDefinition(
    name="qtgql::customscalars::TimeScalar",
    graphql_name="Time",
    deserialized_type="QTime",
    to_qt_type="QString",
    include_path="<qtgql/customscalars/customscalars.hpp>",
)
DecimalScalarDefinition = CustomScalarDefinition(
    name="qtgql::customscalars::DecimalScalar",
    graphql_name="Decimal",
    deserialized_type="QString",
    to_qt_type="QString",
    include_path="<qtgql/customscalars/customscalars.hpp>",
)
CUSTOM_SCALARS: CustomScalarMap = {
    DateTimeScalarDefinition.graphql_name: DateTimeScalarDefinition,
    DateScalarDefinition.graphql_name: DateScalarDefinition,
    TimeScalarDefinition.graphql_name: TimeScalarDefinition,
    DecimalScalarDefinition.graphql_name: DecimalScalarDefinition,
}
