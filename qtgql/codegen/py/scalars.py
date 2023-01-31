from datetime import date, datetime
from decimal import Decimal
from typing import Any, Generic, Optional, Type, TypeVar

T = TypeVar("T")

__all__ = ["BaseCustomScalar", "DateTimeScalar", "BuiltinScalars", "CUSTOM_SCALARS"]


class BaseCustomScalar(Generic[T]):
    """Class to extend by user defined scalars."""

    __slots__ = "_value"
    GRAPHQL_NAME: str
    """The *real* GraphQL name of the scalar (used by the codegen inspection
    pipeline)."""
    DEFAULT_DESERIALIZED: Any = " --- "
    """A place holder graphql query returned null or the field wasn't queried.

    can be used by `from_graphql()`
    """

    def __init__(self, v: T):
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


class DateTimeScalar(BaseCustomScalar[Optional[datetime]]):
    """An ISO-8601 encoded datetime."""

    GRAPHQL_NAME: str = "DateTime"
    DEFAULT_DESERIALIZED = " --- "

    @classmethod
    def from_graphql(cls, v: Optional[str] = None) -> "DateTimeScalar":
        if v:
            return cls(datetime.fromisoformat(v))
        return cls(None)

    def to_qt(self) -> str:
        if self._value:
            return self._value.strftime(" %H:%M: ")
        return self.DEFAULT_DESERIALIZED


class DecimalScalar(BaseCustomScalar[Decimal]):
    """A Decimal value serialized as a string."""

    GRAPHQL_NAME = "Decimal"
    DEFAULT_DESERIALIZED = Decimal()

    @classmethod
    def from_graphql(cls, v: Optional[str] = None) -> "DecimalScalar":
        if v:
            return cls(Decimal(v))
        return cls(cls.DEFAULT_DESERIALIZED)

    def to_qt(self) -> str:
        return str(self._value)


class DateScalar(BaseCustomScalar[Optional[date]]):
    """An ISO-8601 encoded date."""

    GRAPHQL_NAME = "Date"

    @classmethod
    def from_graphql(cls, v: Optional[str] = None) -> "DateScalar":
        if v:
            return cls(date.fromisoformat(v))
        return cls(None)

    def to_qt(self) -> str:
        if self._value:
            return self._value.isoformat()
        return self.DEFAULT_DESERIALIZED


CustomScalarMap = dict[str, Type[BaseCustomScalar]]

CUSTOM_SCALARS: CustomScalarMap = {
    DateTimeScalar.GRAPHQL_NAME: DateTimeScalar,
    DecimalScalar.GRAPHQL_NAME: DecimalScalar,
    DateScalar.GRAPHQL_NAME: DateScalar,
}

BuiltinScalars: dict[str, type] = {
    "Int": int,
    "Float": float,
    "String": str,
    "ID": str,
    "Boolean": bool,
}
