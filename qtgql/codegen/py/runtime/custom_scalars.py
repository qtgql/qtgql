from abc import ABC, abstractmethod
from datetime import date, datetime, time
from typing import Any, Generic, Optional, Type, TypeVar

from _decimal import Decimal

T = TypeVar("T")
T_RAW = TypeVar("T_RAW")
__all__ = ["BaseCustomScalar"]


class BaseCustomScalar(Generic[T, T_RAW], ABC):
    """Class to extend by user defined scalars."""

    __slots__ = "_value"
    GRAPHQL_NAME: str
    """The *real* GraphQL name of the scalar (used by the codegen inspection
    pipeline)."""
    DEFAULT_VALUE: T
    """A place holder graphql query returned null or the field wasn't queried.

    can be used by `from_graphql()`
    """

    def __init__(self, v: Optional[T] = None):
        if not v:
            self._value = self.DEFAULT_VALUE
        else:
            self._value = v

    def parse_value(self) -> T_RAW:
        """When this scalar is used for input types (in variables) this method
        would be called to parse the value to JSON form."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize(cls, v: Optional[T_RAW] = None) -> "BaseCustomScalar":
        """Deserializes data fetched from graphql, This is useful when you want
        to set a first-of value that will later be used by `to_qt()`.

        **must be overridden**!
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def to_qt(self) -> Any:
        """Will be used by the property getter, This is the official value that
        Qt should "understand".

        **must be overridden**!
        """
        raise NotImplementedError  # pragma: no cover

    def __ne__(self, other) -> bool:
        assert isinstance(other, BaseCustomScalar), "can only compare scalar with other scalar."
        return self._value != other._value


class DateTimeScalar(BaseCustomScalar[datetime, str]):
    """An ISO-8601 encoded datetime."""

    GRAPHQL_NAME: str = "DateTime"
    DEFAULT_VALUE = datetime.now()
    FORMAT_STRING = "%H:%M (%m/%d/%Y)"

    def parse_value(self) -> str:
        return self._value.isoformat()

    @classmethod
    def deserialize(cls, v=None) -> "DateTimeScalar":
        if v:
            return cls(datetime.fromisoformat(v))
        return cls()

    def to_qt(self) -> str:
        return self._value.strftime(self.FORMAT_STRING)


class DateScalar(BaseCustomScalar[date, str]):
    """An ISO-8601 encoded date."""

    GRAPHQL_NAME = "Date"
    DEFAULT_VALUE = date(year=1998, month=8, day=23)

    def parse_value(self) -> str:
        return self._value.isoformat()

    @classmethod
    def deserialize(cls, v=None) -> "DateScalar":
        if v:
            return cls(date.fromisoformat(v))
        return cls()

    def to_qt(self) -> str:
        return self._value.isoformat()


class TimeScalar(BaseCustomScalar[time, str]):
    """an ISO-8601 encoded time."""

    GRAPHQL_NAME = "Time"
    DEFAULT_VALUE = time()

    def parse_value(self) -> str:
        return self._value.isoformat()

    @classmethod
    def deserialize(cls, v: Optional[str] = None) -> "TimeScalar":
        if v:
            return cls(time.fromisoformat(v))
        return cls()

    def to_qt(self) -> str:
        return self._value.isoformat()


class DecimalScalar(BaseCustomScalar[Decimal, str]):
    """A Decimal value serialized as a string."""

    GRAPHQL_NAME = "Decimal"
    DEFAULT_VALUE = Decimal()

    def parse_value(self) -> str:
        return str(self._value)

    @classmethod
    def deserialize(cls, v: Optional[str] = None) -> "DecimalScalar":
        if v:
            return cls(Decimal(v))
        return cls()

    def to_qt(self) -> str:
        return str(self._value)


CustomScalarMap = dict[str, Type[BaseCustomScalar]]
CUSTOM_SCALARS: CustomScalarMap = {
    DateTimeScalar.GRAPHQL_NAME: DateTimeScalar,
    DecimalScalar.GRAPHQL_NAME: DecimalScalar,
    DateScalar.GRAPHQL_NAME: DateScalar,
    TimeScalar.GRAPHQL_NAME: TimeScalar,
}
