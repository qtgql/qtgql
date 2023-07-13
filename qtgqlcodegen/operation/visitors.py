from __future__ import annotations

import copy
from typing import TYPE_CHECKING

import graphql
from graphql import OperationType, language as gql_lang
from graphql.language import visitor

from qtgqlcodegen.core.graphql_ref import (
    is_fragment_definition_node,
    is_fragment_spread_node,
    is_operation_def_node,
    is_selection_set,
)
from qtgqlcodegen.operation.definitions import QtGqlFragmentDefinition
from qtgqlcodegen.utils import require

if TYPE_CHECKING:
    from qtgqlcodegen.schema.definitions import SchemaTypeInfo


class UsedFragmentFinder(visitor.Visitor):
    def __init__(self, available_fragments: dict[str, QtGqlFragmentDefinition]) -> None:
        super().__init__()
        self.available_fragments = available_fragments
        self._used_fragments: dict[str, QtGqlFragmentDefinition] = {}

    def enter_fragment_spread(self, node: gql_lang.FragmentSpreadNode, *args, **kwargs) -> None:
        name = node.name.value
        self._used_fragments[name] = self.available_fragments[name]

    @classmethod
    def get_used_fragments(
        cls,
        available_fragments: dict[str, QtGqlFragmentDefinition],
        operation: gql_lang.OperationDefinitionNode,
    ) -> tuple[QtGqlFragmentDefinition, ...]:
        ret = cls(available_fragments)
        graphql.visit(operation, ret)
        return tuple(ret._used_fragments.values())


class OperationsMapper(visitor.Visitor):
    def __init__(
        self,
        type_info: SchemaTypeInfo,
    ):
        super().__init__()
        self.schema_type_info = type_info
        self.operations: dict[str, gql_lang.OperationDefinitionNode] = {}

    def enter_operation_definition(self, node: graphql.Node, *args, **kwargs) -> None:
        if operation := is_operation_def_node(node):
            if operation.operation in (
                OperationType.QUERY,
                OperationType.MUTATION,
                OperationType.SUBSCRIPTION,
            ):
                assert operation.name, "QtGql enforces operations to have names."

                self.operations[operation.name.value] = operation

    @classmethod
    def evaluate(
        cls,
        type_info: SchemaTypeInfo,
        document: gql_lang.DocumentNode,
    ) -> tuple[gql_lang.OperationDefinitionNode, ...]:
        ret = cls(type_info)
        graphql.visit(document, ret)
        return tuple(ret.operations.values())


class FragmentsVisitor(visitor.Visitor):
    """Gets all fragments from the operations file."""

    def __init__(self):
        super().__init__()
        self.fragments: dict[str, QtGqlFragmentDefinition] = {}

    def enter_fragment_definition(self, node: graphql.Node, *args, **kwargs) -> None:
        fragment = require(is_fragment_definition_node(node))
        frag_name = fragment.name.value
        self.fragments[fragment.name.value] = QtGqlFragmentDefinition(
            name=frag_name,
            node=fragment,
        )

    @classmethod
    def get_fragments(cls, document: gql_lang.DocumentNode) -> dict[str, QtGqlFragmentDefinition]:
        ret = cls()
        graphql.visit(document, ret)
        return ret.fragments


class FragSpreadUnzipper(visitor.Visitor):
    def __init__(self, available_fragments: dict[str, QtGqlFragmentDefinition]) -> None:
        super().__init__()
        self.available_fragments = available_fragments

    def enter_fragment_spread(
        self,
        node: gql_lang.FragmentSpreadNode,
        key,
        parent,
        path,
        ancestors,
    ) -> None:
        frag_spread = require(is_fragment_spread_node(node))
        parent_as_list = list(parent)
        parent_as_list.pop(key)
        frag = self.available_fragments[frag_spread.name.value]
        on_selection_set = require(is_selection_set(ancestors[-1]))
        on_selection_set.selections = frag.node.selection_set.selections + tuple(parent_as_list)

    @classmethod
    def unzip_doc(
        cls,
        document: gql_lang.DocumentNode,
        available_fragments: dict[str, QtGqlFragmentDefinition],
    ) -> gql_lang.DocumentNode:
        ret = cls(available_fragments)
        copied_doc = copy.deepcopy(document)
        graphql.visit(copied_doc, ret)
        return copied_doc
