from __future__ import annotations

from typing import List, NamedTuple

import attrs

from qtgql.codegen.py.objecttype import GqlFieldDefinition
from qtgql.codegen.py.runtime.queryhandler import SelectionConfig


@attrs.define
class QtGqlQueriedField(GqlFieldDefinition):
    selection_set: List[QtGqlQueriedField] = attrs.Factory(list)

    @classmethod
    def from_field(cls, f: GqlFieldDefinition) -> QtGqlQueriedField:
        return cls(
            **attrs.asdict(f, recurse=False),
        )

    def as_conf_string(self) -> str:
        if self.selection_set:
            inner_selection = [
                f"'{selection.name}': {selection.as_conf_string()}"
                for selection in self.selection_set
            ]
            inner_selection = "{" + ", ".join(inner_selection) + "}"
            return f"{SelectionConfig.__name__} ({inner_selection})"
        else:
            return "None"


class QtGqlQueryHandlerDefinition(NamedTuple):
    query: str
    name: str
    field: QtGqlQueriedField
    directives: list[str] = []
    fragments: list[str] = []

    @property
    def operation_config(self) -> str:
        return self.field.as_conf_string()
