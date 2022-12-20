from unittest.mock import patch
from uuid import uuid4

import attrs
from attrs import asdict
import pytest
from qtpy import QtCore as qtc

from qter.itemsystem import GenericModel, RoleDoesNotExist, define_roles, role

NORMAL_GQL = "normal_gql"
NORMAL_GQL_CAMELIZED = "normalGql"
NO_CAMEL_CASE = "no_camel_case"
NOT_GQL = "not_gql"
CHILD = "child"
NOT_A_CHILD = "not_a_child"


@define_roles
class FullClass:
    normalGql: int = role()
    no_camel_case: str = role()
    not_gql: str = role(init=False, is_gql=False)
    not_a_role: str = attrs.field(init=False, default=2)
    uuid: str = role(factory=lambda: uuid4().hex)

    @not_gql.default
    def not_gql_factory(self):
        return "not gql factory"


def init_dict_fullClass():
    return {NORMAL_GQL_CAMELIZED: 2, NO_CAMEL_CASE: "dfs"}


@define_roles
class WithChild:
    child: FullClass = role()
    not_a_child: int = role()


def init_dict_withChild():
    return {CHILD: [init_dict_fullClass() for _ in range(3)], NOT_A_CHILD: "not child"}


class Test_roleDefined:
    def test_has_dunder_roles(self):
        assert hasattr(FullClass, "__roles__")

    def test_first_role_is_256(self):
        assert list(FullClass.__roles__.qt_roles.keys())[0] == 256

    def test_not_defined_as_role_is_not_a_role(self):
        assert hasattr(FullClass, "not_a_role")
        assert not hasattr(FullClass.__roles__.by_name, "not_a_role")
        assert not hasattr(FullClass.__roles__.by_name, "notARole")

    def test_role_fields_in_qt_roles(self):
        roles = FullClass.__roles__
        qt_roles = roles.qt_roles
        for num, role_ in roles.by_num.items():
            assert role_.qt_name is qt_roles[num]

    def test_roledefined_annotated_marked_as_child(self):
        roles = WithChild.__roles__
        for _, child in roles.children.items():
            assert child.is_child
        for name, role_ in roles.by_name.items():
            if name not in roles.children:
                assert not role_.is_child

    def test_get_subclassed_model(self):
        assert issubclass(FullClass.Model, GenericModel)

    def test_initialize(self):
        FullClass(**init_dict_fullClass())

    def test_post_init(self):
        @define_roles
        class WithPostInit:
            unit_name: int = role(init=False, is_gql=False, default=4)

            def __attrs_post_init__(self):
                self.unit_name = 2

        assert WithPostInit().unit_name == 2


class TestGenericModel:
    @pytest.fixture
    def full_model(self) -> GenericModel[FullClass]:
        return FullClass.Model([init_dict_fullClass() for _ in range(10)])

    @pytest.fixture
    def model_with_child(self) -> GenericModel[WithChild]:
        return WithChild.Model([init_dict_withChild() for _ in range(3)])

    def test_get_role_names(self):
        @define_roles
        class WithModel:
            class Model(GenericModel):
                ...

            a: int = role()

        assert WithModel.Model([{"a": 2}]).roleNames() is WithModel.__roles__.qt_roles

        @define_roles
        class WithoutModel:
            a: int = role()

        assert WithoutModel.Model([{"a": 2}]).roleNames() is WithoutModel.__roles__.qt_roles

    def test_initialize_create_data(self, full_model):
        model_data = asdict(full_model._data[0])
        assert model_data[NORMAL_GQL_CAMELIZED] == init_dict_fullClass()[NORMAL_GQL_CAMELIZED]
        assert model_data[NO_CAMEL_CASE] == init_dict_fullClass()[NO_CAMEL_CASE]

    def test_get_data_wrong_role_raises_exception(self, full_model):
        with pytest.raises(RoleDoesNotExist):
            full_model.data(full_model.index(0), 0)

    def test_child_creates_model(self, full_model):
        model = WithChild.Model([init_dict_withChild() for _ in range(3)])
        res = model.data(full_model.index(0), WithChild.__roles__.by_name[CHILD].num)
        assert isinstance(res, GenericModel)

    def test_child_model_has_parent_model(self, full_model):
        model = WithChild.Model([init_dict_withChild() for _ in range(3)])
        res = model.data(full_model.index(0), WithChild.__roles__.by_name[CHILD].num)
        assert res.parent() is model

    def test_set_data(self, full_model):
        full_model.setData(full_model.index(0), "VALUE", 256)
        assert full_model._data[0].normalGql == "VALUE"

    def test_flags_return_editable(self, full_model):
        flag = full_model.flags(full_model.index(0))
        assert flag == qtc.Qt.ItemFlag.ItemIsEditable

    def test_invalid_index_returns_no_item_flag(self, full_model):
        flag = full_model.flags(full_model.index(25))
        assert flag == qtc.Qt.ItemFlag.NoItemFlags

    def test_append(self, qtbot):
        m = FullClass.Model()
        inst = FullClass(**init_dict_fullClass())
        with qtbot.wait_signal(m.rowsAboutToBeInserted):
            m.append(inst)
        assert inst in m._data

    def test_pop(self, qtbot, full_model):
        original_data = full_model._data.copy()
        with qtbot.wait_signal(full_model.rowsAboutToBeRemoved):
            full_model.pop(1)

        assert original_data != full_model._data
        original_data.pop(1)
        assert original_data == full_model._data

    @patch("PySide6.QtCore.QAbstractListModel.endRemoveRows")
    def test_clear(self, mock, qtbot, full_model):
        assert full_model.rowCount() > 0
        with qtbot.wait_signal(full_model.rowsAboutToBeRemoved):
            full_model.clear()

        assert full_model.rowCount() == 0
        assert mock.called

    def test_clear_clears_children_as_well(self, model_with_child):
        model = model_with_child
        child = model._data[0].child
        assert len(child._data)
        model.clear()
        assert not len(child._data)

    def test_get_node(self, model_with_child):
        node: FullClass = model_with_child._data[0].child._data[0]
        result = model_with_child.get_node(node.uuid)
        assert result.node == node

    def test_update_node_with_dict(self, model_with_child):
        before: FullClass = model_with_child._data[0].child._data[0]
        TEST_NODE_UPDATE = "TEST_NODE_UPDATE"
        assert before.normalGql != TEST_NODE_UPDATE
        uuid = before.uuid
        to_replace = attrs.evolve(before, **{NORMAL_GQL_CAMELIZED: TEST_NODE_UPDATE})
        to_replace.normalGql = TEST_NODE_UPDATE
        assert before != to_replace
        assert before.uuid == to_replace.uuid
        model_with_child.update_node(uuid, to_replace)
        after_update = model_with_child._data[0].child._data[0]
        assert after_update == to_replace
