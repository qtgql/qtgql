from __future__ import annotations

import uuid
from types import ModuleType
from typing import Any
from typing import Callable
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from qtgql.codegen.objecttype import QtGqlFieldDefinition, QtGqlObjectTypeDefinition


@pytest.fixture()
def tmp_mod():
    return ModuleType(uuid.uuid4().hex)


def generate_type_kwargs(t: QtGqlObjectTypeDefinition, v) -> dict:
    return {p.name: v for p in t.fields}


def property_tester(
    default_types: list[QtGqlObjectTypeDefinition],
    compiled_mod,
    test: Callable[[QtGqlFieldDefinition, Any], None],
):
    for t in default_types:
        cls = getattr(compiled_mod, t.name)
        for prop in t.fields:
            test(prop, cls)
