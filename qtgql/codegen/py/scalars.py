from datetime import datetime
from typing import Any, Generic, Optional, Type, TypeVar

T = TypeVar("T")


class BaseCustomScalar(Generic[T]):
    __slots__ = "_value"
    GRAPHQL_NAME: str

    def __init__(self, v: Optional[T] = None):
        self._value = v

    @classmethod
    def from_graphql(cls, v: Optional[T] = None) -> "BaseCustomScalar[T]":
        raise NotImplementedError

    def to_qt(self) -> Any:
        raise NotImplementedError


class DateTimeScalar(BaseCustomScalar[datetime]):
    GRAPHQL_NAME: str = "DateTime"

    @classmethod
    def from_graphql(cls, v: Optional[str] = None) -> "DateTimeScalar":
        if v:

            return cls(datetime.fromisoformat(v))
        return cls()

    def to_qt(self) -> Optional[str]:
        if self._value:
            return self._value.strftime(" %H:%M: ")
        return None


CustomScalarMap = dict[str, Type[BaseCustomScalar]]

CUSTOM_SCALARS: CustomScalarMap = {DateTimeScalar.GRAPHQL_NAME: DateTimeScalar}

BuiltinScalars: dict[str, type] = {
    "Int": int,
    "Float": float,
    "String": str,
    "ID": str,
    "Boolean": bool,
}
