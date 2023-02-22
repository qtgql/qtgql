from __future__ import annotations

import uuid
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable

import pytest

if TYPE_CHECKING:
    from qtgql.codegen.py.objecttype import GqlFieldDefinition, GqlTypeDefinition


@pytest.fixture()
def tmp_mod():
    return ModuleType(uuid.uuid4().hex)


def generate_type_kwargs(t: GqlTypeDefinition, v) -> dict:
    return {p.name: v for p in t.fields}


def property_tester(
    default_types: list[GqlTypeDefinition],
    compiled_mod,
    test: Callable[[GqlFieldDefinition, Any], None],
):
    for t in default_types:
        cls = getattr(compiled_mod, t.name)
        for prop in t.fields:
            test(prop, cls)
