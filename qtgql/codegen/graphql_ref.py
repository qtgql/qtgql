from __future__ import annotations

from typing import Callable, Optional, Type, TypeVar

from graphql import language as gql_lang
from graphql.type import definition as gql_def

T_AST_Node = TypeVar("T_AST_Node", bound=gql_lang.Node)


def ast_identifier_factory(
    expected: Type[T_AST_Node],
) -> Callable[[gql_lang.Node], Optional[T_AST_Node]]:
    def type_guarder(node: gql_lang.ast.Node) -> Optional[T_AST_Node]:
        if isinstance(node, expected):
            return node

    return type_guarder


is_selection_set = ast_identifier_factory(gql_lang.ast.SelectionSetNode)
is_inline_fragment = ast_identifier_factory(gql_lang.InlineFragmentNode)
is_operation_def_node = ast_identifier_factory(gql_def.OperationDefinitionNode)
is_field_node = ast_identifier_factory(gql_def.FieldNode)
T_Definition = TypeVar("T_Definition", bound=gql_def.GraphQLType)


def definition_identifier_factory(
    expected: Type[T_Definition],
) -> Callable[[gql_def.GraphQLType], Optional[T_Definition]]:
    def type_guarder(definition: gql_def.GraphQLType) -> Optional[T_Definition]:
        if isinstance(definition, expected):
            return definition

    return type_guarder


is_object_definition = definition_identifier_factory(gql_def.GraphQLObjectType)
is_enum_definition = definition_identifier_factory(gql_def.GraphQLEnumType)
is_list_definition = definition_identifier_factory(gql_def.GraphQLList)
is_scalar_definition = definition_identifier_factory(gql_def.GraphQLScalarType)
is_union_definition = definition_identifier_factory(gql_def.GraphQLUnionType)
is_non_null_definition = definition_identifier_factory(gql_def.GraphQLNonNull)
