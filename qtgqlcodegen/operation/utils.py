from __future__ import annotations

import functools
from typing import TYPE_CHECKING

import attrs
from attr import define

from qtgqlcodegen.core.graphql_ref import (
    SelectionsSet,
    is_fragment_spread_node,
)
from qtgqlcodegen.utils import HashAbleDict, _replace_tuple_item

if TYPE_CHECKING:
    from graphql.language import ast as gql_lang


@define
class _UnwrappedSelectionSet:
    """Selection set without fragments and the fragments that were used."""

    selection_set: SelectionsSet
    used_fragments: dict[str, gql_lang.FragmentDefinitionNode] = attrs.Factory(dict)


@functools.lru_cache(None)
def _unwrap_fragment_spread(
    available_fragments: HashAbleDict[str, gql_lang.FragmentDefinitionNode],
    frag: gql_lang.FragmentDefinitionNode,
) -> tuple[dict[str, gql_lang.FragmentDefinitionNode], SelectionsSet]:
    ret: list[gql_lang.SelectionNode] = []
    used_frags: dict[str, gql_lang.FragmentDefinitionNode] = {}
    for node in frag.selection_set.selections:
        # there might be inner fragments.
        if frag_spread := is_fragment_spread_node(node):
            frag = available_fragments[frag_spread.name.value]
            used_frags[frag.name.value] = frag
            res = _unwrap_fragment_spread(available_fragments, frag)
            used_frags.update(res[0])
            ret.extend(res[1])
        else:
            ret.append(node)

    return used_frags, tuple(ret)


def unwrap_frag_spreads(
    available_fragments: HashAbleDict[str, gql_lang.FragmentDefinitionNode],
    selections: SelectionsSet,
    ret: _UnwrappedSelectionSet | None = None,
) -> _UnwrappedSelectionSet:
    if not ret:
        ret = _UnwrappedSelectionSet(selection_set=selections)
    for i, selection in enumerate(ret.selection_set):
        if frag_spread := is_fragment_spread_node(selection):
            resolved = available_fragments[frag_spread.name.value]
            ret.used_fragments[resolved.name.value] = resolved
            used_by_frag, frag_selections = _unwrap_fragment_spread(available_fragments, resolved)
            ret.selection_set = _replace_tuple_item(ret.selection_set, i, frag_selections)
            ret.used_fragments.update(used_by_frag)
    return ret
