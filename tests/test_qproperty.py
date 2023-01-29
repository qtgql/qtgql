from typing import Optional

from PySide6.QtCore import Property, QObject
from qtgql.qproperty import qproperty


def test_builtins():
    class A(QObject):
        @Property(type=int, constant=True)
        def qt(self):
            return 2

        @qproperty(type=int, constant=True)
        def hack(self):
            return 2

    a = A()

    assert a.qt == a.hack


def test_optional():
    """Optional is not supported by PySide6 `Signal`"""

    class A(QObject):
        @Property(type=int, constant=True)
        def qt(self):
            return 2

        @qproperty(type=Optional[int], constant=True)
        def hack(self):
            return 2

    a = A()

    assert a.qt == a.hack
