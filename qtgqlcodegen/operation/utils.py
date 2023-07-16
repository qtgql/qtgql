from __future__ import annotations

import functools
from typing import TYPE_CHECKING

import attrs
from attr import define

from qtgqlcodegen.core.graphql_ref import SelectionsSet, is_fragment_spread_node
from qtgqlcodegen.utils import HashAbleDict, _replace_tuple_item

if TYPE_CHECKING:
    from graphql.language import ast as gql_lang


@define
class _UnwrappedSelectionSet:
    """Selection set without fragments and the fragments that were used."""

    selection_set: SelectionsSet
    used_fragments: dict[str, gql_lang.FragmentDefinitionNode] = attrs.Factory(dict)

    def __hash__(self) -> int:
        # there is no need to hash this.
        return 0


@functools.cache
def _unwrap_frag_spreads(
    available_fragments: HashAbleDict[str, gql_lang.FragmentDefinitionNode],
    selections: SelectionsSet,
    ret: _UnwrappedSelectionSet | None = None,
) -> _UnwrappedSelectionSet:
    if not ret:
        ret = _UnwrappedSelectionSet(selection_set=selections)
    to_replace: list[tuple[int, SelectionsSet]] = []
    for i, selection in enumerate(ret.selection_set):
        if frag_spread := is_fragment_spread_node(selection):
            resolved = available_fragments[frag_spread.name.value]
            ret.used_fragments[resolved.name.value] = resolved
            to_replace.append((i, resolved.selection_set.selections))

    for replacement in to_replace:
        # there might be nested frag spreads.
        unwrapped = _unwrap_frag_spreads(available_fragments, replacement[1])
        ret.selection_set = _replace_tuple_item(selections, replacement[0], unwrapped.selection_set)

    return ret
