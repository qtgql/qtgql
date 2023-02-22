from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from qtgql.codegen.py.objecttype import GqlFieldDefinition


class QueryHandlerDefinition(NamedTuple):
    query: str
    name: str
    field: GqlFieldDefinition
    directives: list[str] = []
    fragments: list[str] = []
