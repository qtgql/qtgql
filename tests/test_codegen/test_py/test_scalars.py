from abc import ABC
from abc import abstractmethod
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timezone
from decimal import Decimal
from typing import Type

from qtgql.codegen.py.runtime.custom_scalars import BaseCustomScalar
from qtgql.codegen.py.runtime.custom_scalars import DateScalar
from qtgql.codegen.py.runtime.custom_scalars import DecimalScalar
from qtgql.codegen.py.runtime.custom_scalars import TimeScalar


class AbstractScalarTestCase(ABC):
    scalar_klass: Type[BaseCustomScalar]

    @abstractmethod
    def test_deserialize(self):
        raise NotImplementedError

    @abstractmethod
    def test_to_qt(self):
        raise NotImplementedError

    def test_default_value(self):
        scalar = self.scalar_klass.deserialize()
        assert scalar._value == scalar.DEFAULT_VALUE
        assert scalar.to_qt() == self.scalar_klass(scalar.DEFAULT_VALUE).to_qt()


class TestDecimalScalar(AbstractScalarTestCase):
    def test_deserialize(self):
        expected = Decimal(1000)
        scalar = DecimalScalar.deserialize(str(expected))
        assert scalar._value == expected

    def test_to_qt(self):
        scalar = DecimalScalar.deserialize("100.0")
        assert scalar.to_qt() == "100.0"

    def test_default_value(self):
        scalar = DecimalScalar.deserialize()
        assert scalar._value == Decimal()
        assert scalar.to_qt() == "0"


class TestDateScalar(AbstractScalarTestCase):
    scalar_klass = DateScalar

    def test_deserialize(self):
        expected = date.fromisoformat(datetime.now(tz=timezone.utc).date().isoformat())
        scalar = DateScalar.deserialize(expected.isoformat())
        assert scalar._value == expected

    def test_to_qt(self):
        scalar = DateScalar(datetime.now(tz=timezone.utc).date())
        assert scalar.to_qt() == datetime.now(tz=timezone.utc).date().isoformat()


class TestTimeScalar(AbstractScalarTestCase):
    scalar_klass = TimeScalar

    def test_deserialize(self):
        expected: time = datetime.now(tz=timezone.utc).time().replace(tzinfo=timezone.utc)
        scalar = TimeScalar.deserialize(expected.isoformat())
        assert scalar._value == expected

    def test_to_qt(self):
        now = datetime.now().time()
        scalar = TimeScalar(now)
        assert scalar.to_qt() == now.isoformat()
