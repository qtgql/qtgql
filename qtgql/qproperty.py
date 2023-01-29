from typing import TYPE_CHECKING, Callable, Optional, TypeVar

from PySide6.QtCore import Property, Signal

from qtgql.typingref import TypeHinter

__all__ = ["qproperty"]

T = TypeVar("T")


def qproperty(
    type: T,
    constant: bool = False,
    fset: Optional[Callable] = None,
    notify: Optional[Signal] = None,
):
    def wrapper(func) -> T:
        ret = TypeHinter.from_annotations(type)
        if ret.is_optional():
            ret = ret.of_type[0]
        return Property(type=ret.type, fset=fset, notify=notify, constant=constant)(func)

    if TYPE_CHECKING:
        return property(wrapper)

    return wrapper
