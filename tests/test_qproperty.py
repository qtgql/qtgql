from typing import Optional

import pytest
from PySide6.QtCore import Property, QObject
from qtgql.tools import qproperty


class PropertyTestCase(QObject):
    def validate(self):
        assert self.property("qt") == self.property("hack")


@pytest.mark.parametrize(
    ("tp", "val"), ((int, 2), (str, "hello"), (float, 1.2), (list, [1, 2, 3]), (dict, {1: 2}))
)
def test_builtins(tp, val):
    class A(PropertyTestCase):
        @Property(type=tp, constant=True)
        def qt(self):
            return val

        @qproperty(constant=True)
        def hack(self) -> tp:
            return val

    a = A()

    a.validate()


def test_optional():
    """Optional is not supported by PySide6 `Signal`."""

    class A(PropertyTestCase):
        @Property(type=int, constant=True)
        def qt(self):
            return 2

        @qproperty(constant=True)
        def hack(self) -> Optional[int]:
            return 2

    a = A()

    a.validate()


def test_custom_type():
    class Foo(QObject):
        ...

    foo_inst = Foo()

    class A(PropertyTestCase):
        @Property(type=Foo, constant=True)
        def qt(self):
            return foo_inst

        @qproperty(constant=True)
        def hack(self) -> Foo:
            return foo_inst

    a = A()

    a.validate()


@pytest.mark.parametrize(
    ("tp", "val"), ((int, 2), (str, "hello"), (float, 1.2), (list, [1, 2, 3]), (dict, {1: 2}))
)
def test_future_annotations(tp, val):
    class A(PropertyTestCase):
        @Property(type=tp, constant=True)
        def qt(self):
            return val

        @qproperty(constant=True)
        def hack(self) -> tp.__name__:
            return val

    a = A()

    a.validate()


class Foo(QObject):
    ...


def test_custom_type_future_annotation(qtbot):
    foo_inst = Foo()

    class A(QObject):
        @Property(type=Foo, constant=True)
        def qt(self):
            return foo_inst

        @qproperty(constant=True)
        def hack(self) -> "Foo":
            return foo_inst

    a = A()

    assert a.qt == a.hack


def test_custom_type_future_annotation_no_ns(qtbot):
    class Bar(QObject):
        ...

    bar_inst = Bar()

    class A(QObject):
        @Property(type=Bar, constant=True)
        def qt(self):
            return bar_inst

        @qproperty(type=Bar, constant=True)
        def hack(self) -> "Bar":
            return bar_inst

    a = A()

    assert a.qt == a.hack


def test_custom_future_annotation_fallback_to_qvariant(qtbot):
    class Bar(QObject):
        ...

    bar_inst = Bar()

    class A(QObject):
        @Property(type=Bar, constant=True)
        def qt(self):
            return bar_inst

        @qproperty(constant=True)
        def hack(self) -> "Bar":
            return bar_inst

    a = A()

    assert a.qt == a.hack
