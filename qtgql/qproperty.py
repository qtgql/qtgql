from typing import Any, Callable, Optional, TypeVar, get_type_hints

from PySide6.QtCore import Property, Signal

from qtgql.typingref import TypeHinter

__all__ = ["qproperty"]

T = TypeVar("T")


def qproperty(
    type: Optional[Any] = None,
    constant: bool = False,
    fset: Optional[Callable] = None,
    notify: Optional[Signal] = None,
):
    type_ = type

    def inner(func: Callable[..., T]) -> T:
        def wrapper() -> func:
            nonlocal type_
            if not type_:
                try:
                    annotation = get_type_hints(func)["return"]
                    ret = TypeHinter.from_annotations(annotation)
                    if ret.is_optional():
                        type_ = ret.of_type[0].type
                    else:
                        type_ = ret.type
                except NameError:
                    type_ = "QVariant"
            return Property(type=type_, fset=fset, notify=notify, constant=constant)(func)

        return wrapper()

    return inner
