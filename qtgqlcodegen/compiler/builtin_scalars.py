from functools import cached_property
from typing import NewType
from typing import Optional

from attr import define

CType = NewType("CType", str)


@define(slots=False)
class BuiltinScalar:
    tp: CType
    defaults_member_name: str
    graphql_name: str
    from_json_convertor: str

    @cached_property
    def default_value(self) -> str:
        return f"qtgql::bases::DEFAULTS::{self.defaults_member_name}"


class _BuiltinScalars:
    INT = BuiltinScalar(
        CType("int"),
        "INT",
        graphql_name="Int",
        from_json_convertor="toInt()",
    )
    FLOAT = BuiltinScalar(
        CType("float"),
        "FLOAT",
        graphql_name="Float",
        from_json_convertor="toDouble()",
    )
    STRING = BuiltinScalar(
        CType("QString"),
        "STRING",
        graphql_name="String",
        from_json_convertor="toString()",
    )
    ID = BuiltinScalar(
        CType("QString"),
        "ID",
        graphql_name="ID",
        from_json_convertor="toString()",
    )
    BOOLEAN = BuiltinScalar(
        CType("bool"),
        "BOOL",
        graphql_name="Boolean",
        from_json_convertor="toBool()",
    )
    UUID = BuiltinScalar(
        CType("QUuid"),
        "UUID",
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

    def keys(self) -> list[str]:
        return [scalar.graphql_name for scalar in self]


BuiltinScalars = _BuiltinScalars()
