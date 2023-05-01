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


class _BuiltinScalars:
    INT = BuiltinScalar(CType("int"), 0, graphql_name="Int")
    FLOAT = BuiltinScalar(CType("float"), 0.0, graphql_name="Float")
    STRING = BuiltinScalar(CType("QString"), " - ", graphql_name="String")
    ID = BuiltinScalar(CType("QString"), "9b2a0828-880d-4023-9909-de067984523c", graphql_name="ID")
    BOOLEAN = BuiltinScalar(CType("bool"), False, graphql_name="Boolean")
    UUID = BuiltinScalar(
        CType("QString"),
        "9b2a0828-880d-4023-9909-de067984523c",
        graphql_name="UUID",
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
