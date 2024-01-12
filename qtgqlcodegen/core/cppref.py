from __future__ import annotations

import copy
import functools
from functools import cached_property, lru_cache
from typing import TYPE_CHECKING, Callable, NamedTuple, TypeVar

import attrs
from attr import define

if TYPE_CHECKING:
    from typing_extensions import Literal, Self, TypeAlias

CppAccessor: TypeAlias = 'Literal["::"] | Literal["."] | Literal["->"]'

T_fn = TypeVar("T_fn", bound=Callable)


def _copy_self(func: T_fn) -> T_fn:
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        self = self.copy()
        return func(self, *args, **kwargs)

    return wrapper  # type: ignore


@define(hash=True, repr=False)
class CppAttribute:
    class ParentCppAttribute(NamedTuple):
        accessor: CppAccessor
        attr: CppAttribute

        def __hash__(self) -> int:
            return hash(self.accessor) + hash(self.attr)

    @define(hash=True)
    class Wrapper:
        start: tuple[str, ...]
        end: tuple[str, ...]

    attr: str
    wrapper: CppAttribute.Wrapper = attrs.field(
        factory=lambda: CppAttribute.Wrapper(tuple(), tuple()),
    )
    parent: CppAttribute.ParentCppAttribute | None = None

    def _as_parent(self, accessor: CppAccessor) -> CppAttribute.ParentCppAttribute:
        return CppAttribute.ParentCppAttribute(
            accessor=accessor,
            attr=self,
        )

    def ns_add(self, inner: str) -> CppAttribute:
        return CppAttribute(
            attr=inner,
            parent=self._as_parent("::"),
        )

    def dot_add(self, inner: str) -> CppAttribute:
        return CppAttribute(
            attr=inner,
            parent=self._as_parent("."),
        )

    def call(self, *args: CppAttribute) -> Self:
        self.wrapper.end += (f"({', '.join((a.build() for a in args))})",)
        return self

    @_copy_self
    def set_template_value(self, value: str) -> Self:
        self.wrapper.end += (f"<{value}>",)
        return self

    @_copy_self
    def as_shared_ptr(self) -> CppAttribute:
        return shared_ptr().set_template_value(self.build())

    @_copy_self
    def as_ptr(self) -> CppAttribute:
        self.wrapper.end += (" *",)
        return self

    @_copy_self
    def as_std_vec(self) -> CppAttribute:
        return std_vec().set_template_value(self.build())

    @_copy_self
    def as_std_list(self) -> CppAttribute:
        return std_list().set_template_value(self.build())

    @_copy_self
    def as_const_ref(self) -> Self:
        self.wrapper.start += ("const ",)
        self.wrapper.end += (" &",)
        return self

    @_copy_self
    def as_const_ptr(self) -> Self:
        self.wrapper.start += ("const ",)
        self.wrapper.end += (" *",)
        return self

    def copy(self):
        return CppAttribute(
            attr=self.attr,
            wrapper=copy.copy(self.wrapper),
            parent=self.parent,
        )

    @lru_cache(maxsize=2 * 300)
    def build(self, prev_val: str = "") -> str:
        ret = f"{' '.join(self.wrapper.start)}{self.attr}{prev_val}{' '.join(self.wrapper.end)}"
        if self.parent:
            accessor = self.parent.accessor
            ret = self.parent.attr.build(accessor + ret)
        return ret

    @cached_property
    def last(self) -> str:
        if self.parent:
            return self.parent.attr.last
        return self.attr

    def __str__(self) -> str:
        return self.build()

    def __repr__(self) -> str:
        return f"<CppAttribute {self.build()}>"


def shared_ptr() -> CppAttribute:
    return CppAttribute(
        attr="std::shared_ptr",
    )


def std_vec() -> CppAttribute:
    return CppAttribute(
        attr="std::vector",
    )


def std_list() -> CppAttribute:
    return CppAttribute(
        attr="std::list",
    )


def QtGqlNs() -> CppAttribute:
    return CppAttribute(
        attr="qtgql",
    )


def QtGqlBasesNs() -> CppAttribute:
    return QtGqlNs().ns_add("bases")


class QtGqlTypes:
    ListModelABC = QtGqlBasesNs().ns_add("ListModelABC")
    NodeInterfaceABC = QtGqlBasesNs().ns_add("NodeInterfaceABC")
    ObjectTypeABC = QtGqlBasesNs().ns_add("ObjectTypeABC")


if __name__ == "__main__":  # pragma: no cover
    QtGqlTypes.ListModelABC.as_shared_ptr().call(CppAttribute("1"), CppAttribute("2"))
    #  TODO: add tests for cppref.py
