from __future__ import annotations

from uuid import uuid4

import pytest
from qtgql.itemsystem import GenericModel, get_base_type, role
from qtgql.itemsystem.core import _BaseType

NORMAL_GQL = "normal_gql"
NORMAL_GQL_CAMELIZED = "normalGql"
NO_CAMEL_CASE = "no_camel_case"
NOT_GQL = "not_gql"
CHILD = "child"
NOT_A_CHILD = "not_a_child"

BaseType = get_base_type()


class FullClass(BaseType):
    normalGql: int = role()
    uuid: str = role(factory=lambda: uuid4().hex)
    parentRef: WithChild = role()


def init_dict_fullClass():
    return {NORMAL_GQL_CAMELIZED: 2}


class WithChild(BaseType):
    uuid: str = role(factory=lambda: uuid4().hex)
    child: GenericModel[FullClass] = role()
    not_a_child: int = role()
    parent_ref: NestedX3 = role()


def init_dict_withChild():
    return {CHILD: [init_dict_fullClass() for _ in range(3)], NOT_A_CHILD: "not child"}


class NestedX3(BaseType):
    childX: list[WithChild] = role()
    uuid: str = role(factory=lambda: uuid4().hex)


def init_dict_nestedX3() -> dict:
    return NestedX3(childX=[WithChild(**init_dict_withChild()) for _ in range(5)]).as_dict()


@pytest.fixture
def base_type(qtbot) -> type[_BaseType]:
    """

    :return: BaseType, this is required to avoid TypeStore conflicts.
    """
    return get_base_type()


@pytest.fixture
def full_model(qtbot, qtmodeltester) -> GenericModel[FullClass]:
    model = FullClass.Model(data=[init_dict_fullClass() for _ in range(10)])
    yield model
    qtmodeltester.check(model, force_py=True)


@pytest.fixture
def model_with_child(qtbot, qtmodeltester) -> GenericModel[WithChild]:
    model = WithChild.Model(data=[init_dict_withChild() for _ in range(3)])
    yield model
    qtmodeltester.check(model)


@pytest.fixture
def nested_model(qtbot, qtmodeltester) -> GenericModel[NestedX3]:
    model = NestedX3.Model(data=[init_dict_nestedX3() for _ in range(3)])
    yield model
    qtbot.check(model)
