from unittest.mock import patch

import pytest
from qtpy import QtCore as qtc

from qtgql.itemsystem import BaseRoleDefined, GenericModel, RoleDoesNotExist, role
from tests.test_itemsystem.fixtures import (
    CHILD,
    FullClass,
    WithChild,
    init_dict_fullClass,
    init_dict_withChild,
)

pytest_plugins = ("tests.test_itemsystem.fixtures",)


def test_get_role_names():
    class Simple(BaseRoleDefined):
        a: int = role()

    assert Simple.Model(schema=None, data=[{"a": 2}]).roleNames() is Simple.__roles__.qt_roles


def test_initialize_create_data(full_model):
    assert full_model._data[0].normalGql == 2


def test_get_data_wrong_role_raises_exception(full_model):
    with pytest.raises(RoleDoesNotExist):
        full_model.data(full_model.index(0), 999)


def test_get_data_wrong_index_returns_None(full_model):
    assert full_model.data(full_model.index(999, 999), 256) is None


def test_child_creates_model(schema, full_model):
    model = WithChild.Model(schema=schema, data=[init_dict_withChild() for _ in range(3)])
    res = model.data(full_model.index(0), WithChild.__roles__.by_name[CHILD].num)
    assert isinstance(res, GenericModel)


def test_child_has_parent_model(schema, full_model):
    parent_model: GenericModel[WithChild] = WithChild.Model(
        schema=schema, data=[init_dict_withChild() for _ in range(3)]
    )
    child_model: GenericModel[FullClass] = parent_model._data[0].child
    assert child_model.parent_model is parent_model


def test_child_model_has_parent_model(schema, full_model):
    model = WithChild.Model(schema=schema, data=[init_dict_withChild() for _ in range(3)])
    res: GenericModel = model.data(full_model.index(0), model.roles.by_name[CHILD].num)
    assert res.parent_model is model


def test_set_data(full_model):
    full_model.setData(full_model.index(0), "VALUE", 256)
    assert full_model._data[0].normalGql == "VALUE"


def test_flags_return_editable(full_model):
    flag = full_model.flags(full_model.index(0))
    assert flag == qtc.Qt.ItemFlag.ItemIsEditable


def test_invalid_index_returns_no_item_flag(full_model):
    flag = full_model.flags(full_model.index(25))
    assert flag == qtc.Qt.ItemFlag.NoItemFlags


def test_append(qtbot, full_model):
    inst = FullClass(**init_dict_fullClass())
    with qtbot.wait_signal(full_model.rowsAboutToBeInserted):
        full_model.append(inst)
    assert inst in full_model._data


def test_pop(qtbot, full_model):
    original_data = full_model._data.copy()
    with qtbot.wait_signal(full_model.rowsAboutToBeRemoved):
        full_model.pop(1)

    assert original_data != full_model._data
    original_data.pop(1)
    assert original_data == full_model._data


@patch("qtpy.QtCore.QAbstractListModel.endRemoveRows")
def test_clear(mock, qtbot, full_model):
    assert full_model.rowCount() > 0
    with qtbot.wait_signal(full_model.rowsAboutToBeRemoved):
        full_model.clear()

    assert full_model.rowCount() == 0
    assert mock.called


def test_clear_clears_children_as_well(model_with_child):
    model = model_with_child
    child = model._data[0].child
    assert len(child._data)
    model.clear()
    assert not len(child._data)
