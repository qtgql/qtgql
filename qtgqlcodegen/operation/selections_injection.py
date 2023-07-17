from __future__ import annotations

from typing import TYPE_CHECKING

from attr import define

from qtgqlcodegen.core.graphql_ref import (
    has_id_selection,
    has_typename_selection,
    inject_id_selection,
    inject_typename_selection,
    is_field_node,
    is_inline_fragment,
)
from qtgqlcodegen.utils import require

if TYPE_CHECKING:
    from graphql import language as gql_lang

    from qtgqlcodegen.schema.definitions import SchemaTypeInfo
    from qtgqlcodegen.types import (
        QtGqlInterface,
        QtGqlObjectType,
        QtGqlTypeABC,
        QtGqlUnion,
    )


@define
class SelectionsStatus:
    id_was_selected: bool = False
    typename_was_selected: bool = False
    """On interfaces inner inline fragments should not be injected if their
    parents was injected."""


def _resolve_union(
    type_info: SchemaTypeInfo,
    ss: gql_lang.SelectionSetNode,
    concrete: QtGqlUnion,
) -> None:
    selection_status = SelectionsStatus()
    if not has_typename_selection(ss):
        inject_typename_selection(ss)
        selection_status.typename_was_selected = True
    for selection in ss.selections:
        if is_field_node(selection):
            continue  # __typename selection
        fragment = is_inline_fragment(selection)
        assert fragment
        type_name = fragment.type_condition.name.value
        # unions support only object types http://spec.graphql.org/October2021/#sec-Unions
        _resolve_type(
            type_info,
            fragment.selection_set,
            require(concrete.get_by_name(type_name)),
        )


def _resolve_interface(
    type_info: SchemaTypeInfo,
    ss: gql_lang.SelectionSetNode,
    concrete: QtGqlInterface,
    selections_status: SelectionsStatus,
) -> None:
    if not selections_status.typename_was_selected and not has_typename_selection(ss):
        inject_typename_selection(ss)
        selections_status.typename_was_selected = True

    if (
        concrete.implements_node
        and not selections_status.id_was_selected
        and not has_id_selection(ss)
    ):
        inject_id_selection(ss)
        selections_status.id_was_selected = True

    for node in ss.selections:
        if inline_frag := is_inline_fragment(node):
            type_name = inline_frag.type_condition.name.value
            concrete_choice = type_info.get_object_or_interface(type_name)
            if inner_interface := concrete_choice.is_interface:
                _resolve_interface(
                    type_info,
                    inline_frag.selection_set,
                    inner_interface,
                    selections_status,
                )
            else:
                _resolve_object(
                    type_info,
                    inline_frag.selection_set,
                    require(concrete_choice.is_object_type),
                    selections_status.id_was_selected,
                )


def _resolve_object(
    type_info: SchemaTypeInfo,
    ss: gql_lang.SelectionSetNode,
    concrete: QtGqlObjectType,
    id_was_selected: bool = False,
) -> None:
    for selection in ss.selections:
        if f := is_field_node(selection):
            if f.selection_set:
                _resolve_type(type_info, f.selection_set, _get_field_type(concrete, f))
            if f.name.value == "id":
                id_was_selected = True

    if concrete.implements_node and not id_was_selected:
        inject_id_selection(ss)


def _get_field_type(
    parent: QtGqlObjectType | QtGqlInterface,
    field: gql_lang.FieldNode,
) -> QtGqlTypeABC:
    return parent.fields_dict[field.name.value].type


def _resolve_type(
    type_info: SchemaTypeInfo,
    ss: gql_lang.SelectionSetNode,
    tp: QtGqlTypeABC,
) -> None:
    if tp.is_model:
        tp = tp.is_model.of_type

    if tp.is_object_type:
        _resolve_object(type_info, ss, tp.is_object_type)
    elif tp.is_interface:
        _resolve_interface(type_info, ss, tp.is_interface, SelectionsStatus())
    elif tp.is_union:
        _resolve_union(type_info, ss, tp.is_union)


def inject_required_selections(
    type_info: SchemaTypeInfo,
    ss: gql_lang.SelectionSetNode,
    concrete: QtGqlObjectType | QtGqlInterface,
) -> None:
    """Qtgql relies on some selections based on some conditions.

    - If a type implements Node it should select `id`
    - If type is an interface it should select `__typename`
    """
    _resolve_type(type_info, ss, concrete)
