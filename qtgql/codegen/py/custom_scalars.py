from datetime import date, datetime, time
from typing import Optional, Type

from _decimal import Decimal

from qtgql.codegen.py.scalars import BaseCustomScalar


class DateTimeScalar(BaseCustomScalar[datetime]):
    """An ISO-8601 encoded datetime."""

    GRAPHQL_NAME: str = "DateTime"
    DEFAULT_VALUE = datetime.now()

    @classmethod
    def from_graphql(cls, v: Optional[str] = None) -> "DateTimeScalar":
        if v:
            return cls(datetime.fromisoformat(v))
        return cls()

    def to_qt(self) -> str:
        return self._value.strftime("%H:%M (%m/%d/%Y)")


class DateScalar(BaseCustomScalar[date]):
    """An ISO-8601 encoded date."""

    GRAPHQL_NAME = "Date"
    DEFAULT_VALUE = date(year=1998, month=8, day=23)

    @classmethod
    def from_graphql(cls, v: Optional[str] = None) -> "DateScalar":
        if v:
            return cls(date.fromisoformat(v))
        return cls()

    def to_qt(self) -> str:
        return self._value.isoformat()


class TimeScalar(BaseCustomScalar[time]):
    """an ISO-8601 encoded time."""

    GRAPHQL_NAME = "Time"
    DEFAULT_VALUE = time()

    @classmethod
    def from_graphql(cls, v: Optional[str] = None) -> "TimeScalar":
        if v:
            return cls(time.fromisoformat(v))
        return cls()

    def to_qt(self) -> str:
        return self._value.isoformat()


class DecimalScalar(BaseCustomScalar[Decimal]):
    """A Decimal value serialized as a string."""

    GRAPHQL_NAME = "Decimal"
    DEFAULT_VALUE = Decimal()

    @classmethod
    def from_graphql(cls, v: Optional[str] = None) -> "DecimalScalar":
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
