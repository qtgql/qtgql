from typing import TYPE_CHECKING, Any, Optional

from qtpy import QtCore as qtc

from qter.autoproperty import define_properties

if TYPE_CHECKING:

    @define_properties
    class Sample:
        a: int
        b: str


class PropertyTestMixin:
    def generate_class(self) -> "Sample":
        raise NotImplementedError

    def test_init(self):
        klass = self.generate_class()
        instance = klass(1, 2)
        assert instance.a == 1
        assert instance.b == 2

    def test_has_property_class(self):
        @define_properties
        class Sample:
            a: int
            b: str

        assert issubclass(Sample.PropertiesClass_, qtc.QObject)

    def test_property_class_initialized_on_init(self):
        klass = self.generate_class()

        instance = klass(1, 2)
        assert isinstance(instance.properties, qtc.QObject)

    def test_property_getter(self):
        klass = self.generate_class()

        instance = klass(1, 2)
        p_class: "Sample" = instance.properties  # type: ignore
        assert p_class.a == instance.a

    def test_property_setter(self):
        klass = self.generate_class()

        instance = klass(1, 2)
        p_class: "Sample" = instance.properties  # type: ignore
        p_class.a = 5
        assert instance.a == 5

    def test_notify_on_setattr(self):
        klass = self.generate_class()

        instance = klass(1, 2)
        p_class: "Sample" = instance.properties  # type: ignore
        reached = False

        def catcher():
            nonlocal reached
            reached = True

        p_class.aChanged.connect(catcher)
        assert p_class.a == 1
        instance.a = 5
        assert p_class.a == 5
        assert reached


class TestAutoProperty(PropertyTestMixin):
    def generate_class(self):
        @define_properties
        class Sample:
            a: int
            b: str

        return Sample


class TestOptionalProperty(PropertyTestMixin):
    def generate_class(self):
        @define_properties
        class Sample:
            a: Optional[int]
            b: Optional[str]

        return Sample


class TestQVariant(PropertyTestMixin):
    def generate_class(self):
        @define_properties
        class Sample:
            a: Any
            b: Any

        return Sample
