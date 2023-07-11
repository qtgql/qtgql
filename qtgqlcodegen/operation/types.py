from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

import graphql
from attr import define

from qtgqlcodegen.types import QtGqlQueriedInterface, QtGqlQueriedObjectType, QtGqlTypeABC

if TYPE_CHECKING:
    from graphql.language import ast as gql_lang


@define(slots=False, repr=False)
class QtGqlFragmentDefinition(QtGqlTypeABC):
    name: str
    ast: gql_lang.FragmentDefinitionNode
    of: QtGqlQueriedObjectType | QtGqlQueriedInterface

    def is_fragment_definition(self) -> QtGqlFragmentDefinition | None:
        return self

    def type_name(self) -> str:
        return self.name

    @property
    def private_name(self) -> str:
        return f"_qtgql_{self.name.lower()}"

    @cached_property
    def as_string(self) -> str:
        return graphql.print_ast(self.ast)

    def __hash__(self) -> int:
        return id(self)
