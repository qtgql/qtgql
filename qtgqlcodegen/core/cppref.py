from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, NamedTuple

import attrs
from attr import define

if TYPE_CHECKING:
    from typing_extensions import Literal, Self, TypeAlias

CppAccessor: TypeAlias = 'Literal["::"] | Literal["."] | Literal["->"]'


@define()
class CppAttribute:
    class ParentCppAttribute(NamedTuple):
        accessor: CppAccessor
        attr: CppAttribute

    @define
    class Wrapper:
        start: str = ""
        end: str = ""

    attr: str
    wrapper: CppAttribute.Wrapper = attrs.field(factory=lambda: CppAttribute.Wrapper())
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

    def call(self, *args: CppAttribute) -> Self:
        self.wrapper.end += f"({', '.join((a.build() for a in args))})"
        return self

    def set_template_value(self, value: str) -> Self:
        if self.parent:
            self.parent.attr.set_template_value(value)
        else:
            self.wrapper.end += f"<{value}>"
        return self

    def as_shared_ptr(self) -> CppAttribute:
        return shared_ptr().set_template_value(self.build())

    def as_const_ref(self) -> CppAttribute:
        return CppAttribute(f"const {self.build()}&")

    def build(self, prev_val: str = "") -> str:
        ret = f"{self.wrapper.start}{self.attr}{prev_val}{self.wrapper.end}"
        if self.parent:
            accessor = self.parent.accessor
            ret = self.parent.attr.build(accessor + ret)
        return ret

    @cached_property
    def name(self) -> str:
        return self.build()

    @cached_property
    def last(self) -> str:
        if self.parent:
            return self.parent.attr.last
        return self.attr


def shared_ptr() -> CppAttribute:
    return CppAttribute(
        attr="std::shared_ptr",
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
