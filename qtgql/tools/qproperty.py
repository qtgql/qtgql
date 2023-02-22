from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Optional,
    TypeVar,
    get_type_hints,
    overload,
)

from PySide6.QtCore import Property, Signal

from qtgql.utils.typingref import TypeHinter

__all__ = ["qproperty"]

R = TypeVar("R")
if TYPE_CHECKING:  # pragma: no cover

    class qproperty_(property, Generic[R]):
        fget: Callable[[Any], R]
        fset: Optional[Callable[[Any, R], None]]
        fdel: Optional[Callable[[Any], None]]

        def __new__(
            cls,
            fget: Callable[[Any], R],
            fset: Optional[Callable[[Any, R], None]] = ...,
            fdel: Optional[Callable[[Any], None]] = ...,
        ) -> qproperty_[R]:
            ...

        @overload  # type: ignore
        def __get__(self, obj: None, type_: Optional[type] = ...) -> qproperty_[R]:
            ...

        @overload
        def __get__(self, obj: object, type_: Optional[type] = ...) -> R:
            ...

        def __set__(self, obj: Any, value: R) -> None:
            ...


def qproperty(
    type: Any = None,
    constant: bool = False,
    fset: Optional[Callable] = None,
    notify: Optional[Signal] = None,
) -> Callable[[Callable[[Any], R]], qproperty_[R]]:
    type_ = type

    def wrapper(func: Callable[[Any], R]) -> qproperty_[R]:
        nonlocal type_
        if not type_:
            try:
                annotation = get_type_hints(func)["return"]
                ret = TypeHinter.from_annotations(annotation)
                type_ = ret.of_type[0].type if ret.is_optional() else ret.type
            except NameError:
                type_ = "QVariant"
        return Property(type=type_, fset=fset, notify=notify, constant=constant)(func)  # type: ignore

    return wrapper
