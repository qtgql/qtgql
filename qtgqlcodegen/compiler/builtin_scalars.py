from typing import Any
from typing import NewType
from typing import Optional

from attr import define

CType = NewType("CType", str)


@define
class BuiltinScalar:
    tp: CType
    default_value: Any
    graphql_name: str
    from_json_convertor: str


class _BuiltinScalars:
    INT = BuiltinScalar(
        CType("int"),
        "qtgql::DEFAULTS::INT",
        graphql_name="Int",
        from_json_convertor="toInt()",
    )
    FLOAT = BuiltinScalar(
        CType("float"),
        "qtgql::DEFAULTS::FLOAT",
        graphql_name="Float",
        from_json_convertor="toDouble()",
    )
    STRING = BuiltinScalar(
        CType("QString"),
        "qtgql::DEFAULTS::STRING",
        graphql_name="String",
        from_json_convertor="toString()",
    )
    ID = BuiltinScalar(
        CType("QString"),
        "qtgql::DEFAULTS::ID",
        graphql_name="ID",
        from_json_convertor="toString()",
    )
    BOOLEAN = BuiltinScalar(
        CType("bool"),
        "qtgql::DEFAULTS::BOOL",
        graphql_name="Boolean",
        from_json_convertor="toBool()",
    )
    UUID = BuiltinScalar(
        CType("QUuid"),
        "qtgql::DEFAULTS::UUID",
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
