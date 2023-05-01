import dataclasses
from functools import cached_property
from typing import ClassVar


@dataclasses.dataclass
class CppNamedType:
    type_name: str
    namespace: ClassVar[str] = ""

    @cached_property
    def name(self) -> str:
        return self.namespace + self.type_name


class QtGqlNamedType(CppNamedType):
    namespace = "qtgql::"


class QtGqlTypes:
    QGraphQLList = QtGqlNamedType("QGraphQLList")
