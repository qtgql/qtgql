from uuid import uuid4

import attrs
import pytest
from attrs import asdict

from qtgql.itemsystem.schema import Schema
from qtgql.typingref import UNSET
from qtgql.itemsystem import GenericModel, role, BaseRoleDefined

NORMAL_GQL = "normal_gql"
NORMAL_GQL_CAMELIZED = "normalGql"
NO_CAMEL_CASE = "no_camel_case"
NOT_GQL = "not_gql"
CHILD = "child"
NOT_A_CHILD = "not_a_child"


class FullClass(BaseRoleDefined):
    normalGql: int = role()
    uuid: str = role(factory=lambda: uuid4().hex)
    parent_ref: 'WithChild' = role()





def init_dict_fullClass():
    return {NORMAL_GQL_CAMELIZED: 2}


class WithChild(BaseRoleDefined):
    uuid: str = role(factory=lambda: uuid4().hex)
    child: list[FullClass] = role()
    not_a_child: int = role()
    parent_ref: 'NestedX3' = role()


def init_dict_withChild():
    return {CHILD: [init_dict_fullClass() for _ in range(3)], NOT_A_CHILD: "not child"}


class NestedX3(BaseRoleDefined):
    childX: GenericModel[WithChild] = role()
    uuid: str = role(factory=lambda: uuid4().hex)

def init_dict_nestedX3() -> dict:
    return asdict(NestedX3(childX=[WithChild(**init_dict_withChild()) for _ in range(5)]))

@pytest.fixture(scope='session')
def schema():
    return Schema(query=NestedX3)

@pytest.fixture
def full_model(qtbot,schema, qtmodeltester) -> GenericModel[FullClass]:
    model = FullClass.Model(schema=schema, data=[init_dict_fullClass() for _ in range(10)])
    yield model
    qtmodeltester.check(model, force_py=True)


@pytest.fixture
def model_with_child(qtbot, schema, qtmodeltester) -> GenericModel[WithChild]:
    model = WithChild.Model(schema=schema, data=[init_dict_withChild() for _ in range(3)])
    yield model
    qtmodeltester.check(model)


@pytest.fixture
def nested_model(qtbot,schema, qtmodeltester) -> GenericModel[NestedX3]:
    model = NestedX3.Model(schema=schema, data=[init_dict_nestedX3() for _ in range(3)])
    yield model
    qtbot.check(model)


