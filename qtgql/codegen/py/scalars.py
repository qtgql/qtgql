from datetime import datetime
from typing import Any, Optional, Type, TypeVar

T = TypeVar("T")


class BaseCustomScalar:
    __slots__ = "_value"
    GRAPHQL_NAME: str
    DEFAULT_DESERIALIZED: Any = ""

    def __init__(self, v: Optional[Any] = None):
        self._value = v

    @classmethod
    def from_graphql(cls, v: Optional[Any] = None) -> "BaseCustomScalar":
        raise NotImplementedError

    def to_qt(self) -> Any:
        raise NotImplementedError


class DateTimeScalar(BaseCustomScalar):
    GRAPHQL_NAME: str = "DateTime"
    DEFAULT_DESERIALIZED = " --- "

    @classmethod
    def from_graphql(cls, v: Optional[str] = None) -> "DateTimeScalar":
        if v:

            return cls(datetime.fromisoformat(v))
        return cls()

    def to_qt(self) -> str:
        if self._value:
            return self._value.strftime(" %H:%M: ")
        return self.DEFAULT_DESERIALIZED


CustomScalarMap = dict[str, Type[BaseCustomScalar]]

CUSTOM_SCALARS: CustomScalarMap = {DateTimeScalar.GRAPHQL_NAME: DateTimeScalar}

BuiltinScalars: dict[str, type] = {
    "Int": int,
    "Float": float,
    "String": str,
    "ID": str,
    "Boolean": bool,
}
