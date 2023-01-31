from datetime import datetime
from typing import Any, Generic, Optional, Type, TypeVar

T = TypeVar("T")

__all__ = ["BaseCustomScalar", "DateTimeScalar", "BuiltinScalars", "CUSTOM_SCALARS"]


class BaseCustomScalar(Generic[T]):
    """Class to extend by user defined scalars."""

    __slots__ = "_value"
    GRAPHQL_NAME: str
    """The *real* GraphQL name of the scalar (used by the codegen inspection
    pipeline)."""
    DEFAULT_DESERIALIZED: Any = ""
    """A place holder graphql query returned null or the field wasn't
    queried."""

    def __init__(self, v: Optional[T] = None):
        self._value = v

    @classmethod
    def from_graphql(cls, v: Optional[Any] = None) -> "BaseCustomScalar":
        """Deserializes data fetched from graphql, This is useful when you want
        to set a first-of value that will later be used by `to_qt()`.

        **must be overridden**!
        """
        raise NotImplementedError  # pragma: no cover

    def to_qt(self) -> Any:
        """Will be used by the property getter, This is the official value that
        Qt should "understand".

        **must be overridden**!
        """
        raise NotImplementedError  # pragma: no cover


class DateTimeScalar(BaseCustomScalar[datetime]):
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
