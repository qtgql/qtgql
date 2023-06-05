from __future__ import annotations

from functools import cached_property
from typing import Optional
from typing import TYPE_CHECKING

from attr import define

if TYPE_CHECKING:
    from typing_extensions import Self


@define
class NameSpaceBuilder:
    ns: str
    inner: Optional[NameSpaceBuilder] = None

    def add(self, inner: NameSpaceBuilder) -> Self:
        if self.inner:
            self.inner.add(inner)
        else:
            self.inner = inner
        return self

    def build(self) -> str:
        if self.inner:
            return f"{self.ns}::{self.inner.build()}"
        return self.ns


def QtGqlNs() -> NameSpaceBuilder:
    return NameSpaceBuilder(
        ns="qtgql",
    )


def QtGqlBasesNs() -> NameSpaceBuilder:
    return QtGqlNs().add(NameSpaceBuilder("bases"))


@define(slots=False)
class CppNamedType:
    namespace: NameSpaceBuilder
    type_name: str

    @cached_property
    def name(self) -> str:
        return self.namespace.add(NameSpaceBuilder(self.type_name)).build()


class QtGqlTypes:
    QGraphQLList = CppNamedType(QtGqlBasesNs(), "ListModelABC")
    ObjectTypeABCWithID = CppNamedType(QtGqlBasesNs(), "ObjectTypeABCWithID")
    ObjectTypeABC = CppNamedType(QtGqlBasesNs(), "ObjectTypeABC")
