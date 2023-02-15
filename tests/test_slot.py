from typing import Any, Optional, Type

import pytest
from attr import define
from PySide6.QtCore import QMetaMethod, QObject, Signal, Slot
from qtgql.tools import slot


class QObjectHelper(QObject):
    def qt(self):
        raise NotImplementedError

    def hack(self):
        raise NotImplementedError

    def slot_by_name(self, name: str) -> list[QMetaMethod]:
        meta = self.metaObject()
        methods = []
        for i in range(meta.methodCount()):
            methods.append(meta.method(i))
        ret = []
        for method in methods:
            m_name = method.name()
            if m_name == name:
                ret.append(method)

        if ret:
            return ret
        raise NameError("not found slot")

    def default_test(self, *params) -> None:
        qt = self.slot_by_name("qt")
        hack = self.slot_by_name("hack")
        compare(qt, hack)
        if params:
            assert self.qt(*params) == self.hack(*params)
        else:
            assert self.qt() == self.hack()


@define
class _SignatureHelper:
    result: Type = [int, str, bool, QObject, list, dict]
    arguments: list[Type] = [int, str, bool, QObject, list, dict]
    parameters: list[Type[Any]] = [1, "test", False, QObject(), [1, 2], {"a": 2}]


SignatureDefault = _SignatureHelper()


def compare(qt: list[QMetaMethod], hack: list[QMetaMethod]):
    assert len(qt) == len(hack)
    for qt_, hack_ in zip(qt, hack):
        name1 = qt_.name().toStdString()
        name2 = hack_.name().toStdString()
        signature1 = qt_.methodSignature().toStdString().strip(name1)
        signature2 = hack_.methodSignature().toStdString().strip(name2)
        assert signature1 == signature2
        assert qt_.returnType() == hack_.returnType()


def test_slot_no_args_no_result():
    class T(QObjectHelper):
        @Slot()
        def qt(self):
            return 2

        @slot
        def hack(self):
            return 2

    T().default_test()


@pytest.mark.parametrize("ret", [SignatureDefault.result])
def test_slot_return(ret):
    class T(QObjectHelper):
        @Slot(result=ret)
        def qt(self):
            return ret

        @slot
        def hack(self) -> ret:
            return ret

    T().default_test()


@pytest.mark.parametrize(
    "arg,param", list(zip(SignatureDefault.arguments, SignatureDefault.parameters))
)
def test_slot_argument(arg, param):
    class T(QObjectHelper):
        @Slot(arg)
        def qt(self, a):
            assert isinstance(a, arg)

        @slot
        def hack(self, a: arg):
            assert isinstance(a, arg)

    T().default_test(param)


@pytest.mark.parametrize(
    "arg,param", list(zip(SignatureDefault.arguments, SignatureDefault.parameters))
)
def test_slot_argument_result(arg, param):
    class T(QObjectHelper):
        @Slot(arg, result=arg)
        def qt(self, a):
            return a

        @slot
        def hack(self, a: arg) -> arg:
            return a

    T().default_test(param)


@pytest.mark.parametrize(
    "arg,param", list(zip(SignatureDefault.arguments, SignatureDefault.parameters))
)
def test_generic_alias(qtbot, arg, param):
    class T(QObjectHelper):
        sig = Signal(list)

        def __init__(self, parent=None):
            super().__init__(parent)
            self.sig.connect(self.qt)
            self.sig.connect(self.hack)
            self.qt_res = None
            self.hack_res = None

        @Slot(list)
        def qt(self, a):
            self.qt_res = a
            assert isinstance(a[0], arg)

        @slot
        def hack(self, a: list[arg]):
            self.hack_res = a
            assert isinstance(a[0], arg)

    t = T()
    to_emit = [param, param]

    t.default_test(
        [
            param,
        ]
    )
    t.sig.emit(to_emit)
    qtbot.wait(100)
    assert t.qt_res == t.hack_res == to_emit


def test_optional_slot_argument(qtbot):
    class T(QObjectHelper):
        default = Signal()
        withArg = Signal(str)

        def __init__(self, parent=None):
            super().__init__(parent)
            self.default.connect(self.qt)
            self.withArg.connect(self.qt)
            self.default.connect(self.hack)
            self.withArg.connect(self.hack)
            self.qt_result = None
            self.hack_result = None

        @Slot(str)
        @Slot()
        def qt(self, a="default"):
            self.qt_result = a

        @slot
        def hack(self, a: Optional[str] = "default") -> None:
            self.hack_result = a

    t = T()
    qtbot.wait(100)
    t.default.emit()
    qtbot.wait(100)
    assert t.qt_result == "default"
    assert t.hack_result == "default"
    t.withArg.emit("test")
    qtbot.wait(100)
    assert t.qt_result == "test"
    assert t.hack_result == "test"

    T().default_test()


def test_optional_with_generic_alias(qtbot):
    class T(QObjectHelper):
        default = Signal()
        withArg = Signal(str)

        def __init__(self, parent=None):
            super().__init__(parent)
            self.default.connect(self.qt)
            self.withArg.connect(self.qt)
            self.default.connect(self.hack)
            self.withArg.connect(self.hack)
            self.qt_result: Optional[list[str]] = None
            self.hack_result: Optional[list[str]] = None

        @Slot(list)
        @Slot(None)
        def qt(self, a="default"):
            self.qt_result = [
                a,
            ]

        @slot
        def hack(self, a: Optional[list[str]] = "default") -> None:
            self.hack_result = [
                a,
            ]

    t = T()
    qtbot.wait(100)
    t.default.emit()
    qtbot.wait(100)
    assert t.qt_result[0] == "default"
    assert t.hack_result[0] == "default"
    t.withArg.emit("test")
    qtbot.wait(100)
    assert t.qt_result[0] == "test"
    assert t.hack_result[0] == "test"

    T().default_test()


@pytest.mark.parametrize("ret", [SignatureDefault.parameters])
def test_Qvariant(ret):
    class T(QObjectHelper):
        @Slot(result="QVariant")
        def qt(self):
            return ret

        @slot
        def hack(self) -> Any:
            return ret

    T().default_test()
