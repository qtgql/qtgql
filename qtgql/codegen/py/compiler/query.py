from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from qtgql.codegen.py.objecttype import GqlFieldDefinition

if TYPE_CHECKING:
    from qtgql.codegen.introspection import OperationName


class QueryHandlerDefinition(NamedTuple):
    query: str
    name: OperationName
    field: GqlFieldDefinition
    directives: list[str] = []
    fragments: list[str] = []
