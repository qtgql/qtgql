from __future__ import annotations

from typing import TYPE_CHECKING

from qtgqlcodegen.core.graphql_ref import is_fragment_spread_node

if TYPE_CHECKING:
    from graphql import language as gql_lang

    from qtgqlcodegen.operation.definitions import OperationTypeInfo


def _replace_tuple_item(
    original: tuple,
    at: int,
    replace: tuple,
):
    return original[0:at] + replace + original[at + 1 : len(original)]


# TODO: cache this.
def unwrap_frag_spreads(
    type_info: OperationTypeInfo,
    selection_set: gql_lang.SelectionSetNode,
) -> gql_lang.SelectionSetNode:
    to_replace: list[tuple[int, gql_lang.SelectionSetNode]] = []
    for i, selection in enumerate(selection_set.selections):
        if frag_spread := is_fragment_spread_node(selection):
            resolved = type_info.raw_fragments[frag_spread.name.value]
            to_replace.append((i, resolved.selection_set))

    ret = selection_set
    for replacement in to_replace:
        # there might be nested frag spreads.
        unwrapped = unwrap_frag_spreads(type_info, replacement[1])
        ret.selections = _replace_tuple_item(ret.selections, replacement[0], unwrapped.selections)

    return ret
