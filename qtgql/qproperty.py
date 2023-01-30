from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar, get_type_hints, overload

from PySide6.QtCore import Property, Signal

from qtgql.typingref import TypeHinter

__all__ = ["qproperty"]

R = TypeVar("R")
if TYPE_CHECKING:  # pragma: no cover

    class qproperty_(property, Generic[R]):
        fget: Callable[[Any], R]
        fset: Callable[[Any, R], None] | None
        fdel: Callable[[Any], None] | None

        def __new__(
            cls,
            fget: Callable[[Any], R],
            fset: Callable[[Any, R], None] | None = ...,
            fdel: Callable[[Any], None] | None = ...,
        ) -> qproperty_[R]:
            ...

        @overload  # type: ignore
        def __get__(self, obj: None, type_: type | None = ...) -> qproperty_[R]:
            ...

        @overload
        def __get__(self, obj: object, type_: type | None = ...) -> R:
            ...

        def __set__(self, obj: Any, value: R) -> None:
            ...


def qproperty(
    type: Any | None = None,
    constant: bool = False,
    fset: Callable | None = None,
    notify: Signal | None = None,
) -> Callable[[Callable[[Any], R]], qproperty_[R]]:
    type_ = type

    def wrapper(func: Callable[[Any], R]) -> qproperty_[R]:
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
        return Property(type=type_, fset=fset, notify=notify, constant=constant)(func)  # type: ignore

    return wrapper
