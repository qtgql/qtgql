from datetime import date, datetime, time
from typing import Optional, Type

from _decimal import Decimal

from qtgql.codegen.py.scalars import BaseCustomScalar


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


class TimeScalar(BaseCustomScalar[Optional[time]]):
    """an ISO-8601 encoded time."""

    GRAPHQL_NAME = "Time"

    @classmethod
    def from_graphql(cls, v: Optional[str] = None) -> "TimeScalar":
        if v:
            return cls(time.fromisoformat(v))
        return cls(None)

    def to_qt(self) -> str:
        if self._value:
            return self._value.isoformat()
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


CustomScalarMap = dict[str, Type[BaseCustomScalar]]
CUSTOM_SCALARS: CustomScalarMap = {
    DateTimeScalar.GRAPHQL_NAME: DateTimeScalar,
    DecimalScalar.GRAPHQL_NAME: DecimalScalar,
    DateScalar.GRAPHQL_NAME: DateScalar,
    TimeScalar.GRAPHQL_NAME: TimeScalar,
}
