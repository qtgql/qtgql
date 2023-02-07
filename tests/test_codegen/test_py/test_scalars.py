from abc import ABC, abstractmethod
from datetime import date, datetime, time
from decimal import Decimal
from typing import Type

from qtgql.codegen.py.custom_scalars import DateScalar, DecimalScalar, TimeScalar
from qtgql.codegen.py.scalars import BaseCustomScalar


class AbstractScalarTestCase(ABC):
    scalar_klass: Type[BaseCustomScalar]

    @abstractmethod
    def test_deserialize(self):
        raise NotImplementedError

    @abstractmethod
    def test_to_qt(self):
        raise NotImplementedError

    def test_default_value(self):
        scalar = self.scalar_klass.from_graphql()
        assert scalar._value == scalar.DEFAULT_VALUE
        assert scalar.to_qt() == self.scalar_klass(scalar.DEFAULT_VALUE).to_qt()


class TestDecimalScalar(AbstractScalarTestCase):
    def test_deserialize(self):
        expected = Decimal(1000)
        scalar = DecimalScalar.from_graphql(str(expected))
        assert scalar._value == expected

    def test_to_qt(self):
        scalar = DecimalScalar.from_graphql("100.0")
        assert scalar.to_qt() == "100.0"

    def test_default_value(self):
        scalar = DecimalScalar.from_graphql()
        assert scalar._value == Decimal()
        assert scalar.to_qt() == "0"


class TestDateScalar(AbstractScalarTestCase):
    scalar_klass = DateScalar

    def test_deserialize(self):
        expected = date.fromisoformat(date.today().isoformat())
        scalar = DateScalar.from_graphql(expected.isoformat())
        assert scalar._value == expected

    def test_to_qt(self):
        scalar = DateScalar(date.today())
        assert scalar.to_qt() == date.today().isoformat()


class TestTimeScalar(AbstractScalarTestCase):
    scalar_klass = TimeScalar

    def test_deserialize(self):
        expected: time = datetime.now().time()
        scalar = TimeScalar.from_graphql(expected.isoformat())
        assert scalar._value == expected

    def test_to_qt(self):
        now = datetime.now().time()
        scalar = TimeScalar(now)
        assert scalar.to_qt() == now.isoformat()
