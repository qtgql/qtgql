from abc import ABC, abstractmethod
from decimal import Decimal

from qtgql.codegen.py.scalars import DecimalScalar


class AbstractScalarTestCase(ABC):
    @abstractmethod
    def test_deserialize(self):
        raise NotImplementedError

    @abstractmethod
    def test_to_qt(self):
        raise NotImplementedError

    @abstractmethod
    def test_default_value(self):
        raise NotImplementedError


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
