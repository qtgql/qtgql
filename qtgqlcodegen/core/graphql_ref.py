from __future__ import annotations

from typing import Callable, TypeVar

from graphql import language as gql_lang
from graphql.type import definition as gql_def

T_AST_Node = TypeVar("T_AST_Node", bound=gql_lang.Node)


def ast_identifier_factory(
    expected: type[T_AST_Node],
) -> Callable[[gql_lang.Node], T_AST_Node | None]:
    def type_guarder(node: gql_lang.ast.Node) -> T_AST_Node | None:
        if isinstance(node, expected):
            return node

    return type_guarder


is_selection_set = ast_identifier_factory(gql_lang.ast.SelectionSetNode)
is_inline_fragment = ast_identifier_factory(gql_lang.InlineFragmentNode)
is_operation_def_node = ast_identifier_factory(gql_def.OperationDefinitionNode)
is_field_node = ast_identifier_factory(gql_def.FieldNode)
is_nonnull_node = ast_identifier_factory(gql_lang.NonNullTypeNode)
is_named_type_node = ast_identifier_factory(gql_lang.NamedTypeNode)


T_Definition = TypeVar("T_Definition", bound=gql_def.GraphQLType)


def definition_identifier_factory(
    expected: type[T_Definition],
) -> Callable[[gql_def.GraphQLType], T_Definition | None]:
    def type_guarder(definition: gql_def.GraphQLType) -> T_Definition | None:
        if isinstance(definition, expected):
            return definition

    return type_guarder


is_object_definition = definition_identifier_factory(gql_def.GraphQLObjectType)
is_enum_definition = definition_identifier_factory(gql_def.GraphQLEnumType)
is_list_definition = definition_identifier_factory(gql_def.GraphQLList)
is_scalar_definition = definition_identifier_factory(gql_def.GraphQLScalarType)
is_union_definition = definition_identifier_factory(gql_def.GraphQLUnionType)
is_non_null_definition = definition_identifier_factory(gql_def.GraphQLNonNull)
is_input_definition = definition_identifier_factory(gql_def.GraphQLInputObjectType)
is_interface_definition = definition_identifier_factory(gql_def.GraphQLInterfaceType)


ID_SELECTION_NODE = (
    gql_lang.FieldNode(name=gql_lang.NameNode(value="id"), arguments=(), directives=()),
)

TYPENAME_SELECTION_NODE = (
    gql_lang.FieldNode(name=gql_lang.NameNode(value="__typename"), arguments=(), directives=()),
)


def inject_selection_factory(
    node: tuple[gql_lang.FieldNode],
) -> Callable[[gql_lang.SelectionSetNode], None]:
    def injector(selection_set: gql_lang.SelectionSetNode) -> None:
        selection_set.selections += node

    return injector


inject_id_selection = inject_selection_factory(ID_SELECTION_NODE)
inject_typename_selection = inject_selection_factory(TYPENAME_SELECTION_NODE)


def selection_set_search_factory(
    selection_name: str,
) -> Callable[[gql_lang.SelectionSetNode], bool]:
    def factory(selection_set: gql_lang.SelectionSetNode):
        for field in selection_set.selections:
            assert isinstance(field, gql_lang.FieldNode), f"{field} is not a field"
            if field.name.value == selection_name:
                return True
        return False

    return factory


has_id_selection = selection_set_search_factory("id")
has_typename_selection = selection_set_search_factory("__typename")
