from typing import Any, Optional

from attr import define


@define
class BuiltinScalar:
    tp: type
    default_value: Any
    graphql_name: str


class _BuiltinScalars:
    INT = BuiltinScalar(int, 0, graphql_name="Int")
    FLOAT = BuiltinScalar(float, 0.0, graphql_name="Float")
    STRING = BuiltinScalar(str, " - ", graphql_name="String")
    ID = BuiltinScalar(str, "9b2a0828-880d-4023-9909-de067984523c", graphql_name="ID")
    BOOLEAN = BuiltinScalar(bool, False, graphql_name="Boolean")
    UUID = BuiltinScalar(str, "9b2a0828-880d-4023-9909-de067984523c", graphql_name="UUID")

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
