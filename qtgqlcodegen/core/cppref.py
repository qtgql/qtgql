from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Literal, NamedTuple

from attr import define

if TYPE_CHECKING:
    from typing_extensions import Self


CppAccessor = Literal["::"] | Literal["."] | Literal["->"]


@define(slots=False)
class CppAttribute:
    class InnerCppAttribute(NamedTuple):
        accessor: CppAccessor
        attr: CppAttribute

        @classmethod
        def create(cls, accessor: CppAccessor, attr: str) -> Self:
            return cls(
                accessor=accessor,
                attr=CppAttribute(attr),
            )

    attr: str
    inner: CppAttribute.InnerCppAttribute | None = None

    def ns_add(self, inner: str) -> Self:
        if self.inner:
            self.inner.attr.ns_add(inner)
        else:
            self.inner = CppAttribute.InnerCppAttribute.create(
                "::",
                inner,
            )
        return self

    def build(self) -> str:
        if self.inner:
            return f"{self.attr}{self.inner.accessor}{self.inner.attr.build()}"
        return self.attr

    @cached_property
    def name(self) -> str:
        return self.build()


def QtGqlNs() -> CppAttribute:
    return CppAttribute(
        attr="qtgql",
    )


def QtGqlBasesNs() -> CppAttribute:
    return QtGqlNs().ns_add("bases")


class QtGqlTypes:
    QGraphQLList = QtGqlBasesNs().ns_add("ListModelABC")
    NodeInterfaceABC = QtGqlBasesNs().ns_add("NodeInterfaceABC")
    ObjectTypeABC = QtGqlBasesNs().ns_add("ObjectTypeABC")
