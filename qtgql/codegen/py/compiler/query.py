from __future__ import annotations

from typing import NamedTuple

from qtgql.codegen.py.objecttype import GqlFieldDefinition


class QueryHandlerDefinition(NamedTuple):
    query: str
    name: str
    field: GqlFieldDefinition
    directives: list[str] = []
    fragments: list[str] = []
