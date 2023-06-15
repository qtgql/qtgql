from functools import cached_property
from typing import Optional

from qtgqlcodegen.core.cppref import CppAttribute, QtGqlBasesNs
from qtgqlcodegen.schema.typing import BuiltinScalar


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

    def by_graphql_name(self, name: str) -> Optional[BuiltinScalar]:
        for scalar in self:
            if scalar.graphql_name == name:
                return scalar

    @cached_property
    def keys(self) -> list[str]:
        return [scalar.graphql_name for scalar in self]


BuiltinScalars = _BuiltinScalars()
