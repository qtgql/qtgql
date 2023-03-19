from __future__ import annotations

from unittest.mock import patch

import pytest
from PySide6 import QtCore
from qtgql.tools.itemsystem import GenericModel, RoleDoesNotExist, RoleMapper, role

from tests.test_itemsystem.conftest import (
    CHILD,
    FullClass,
    WithChild,
    init_dict_fullClass,
    init_dict_withChild,
)


def test_has_dunder_roles(full_model):
    assert isinstance(full_model.__roles__, RoleMapper)


def test_first_role_is_256(full_model):
    assert list(full_model.__roles__.qt_roles.keys())[0] == 256


def test_annotated_with_GenericModel_in_childre_dict(model_with_child):
    roles = model_with_child.__roles__
    assert roles.children
    assert roles.children["child"] is FullClass


def test_role_fields_in_qt_roles(full_model):
    roles = full_model.__roles__
    qt_roles = roles.qt_roles
    for num, role_ in roles.by_num.items():
        assert role_.qt_name is qt_roles[num]


def test_get_role_names(base_type):
    class Simple(base_type):
        a: int = role()

    assert Simple.Model(data=[{"a": 2}]).roleNames() is Simple.Model.__roles__.qt_roles


def test_initialize_create_data(full_model):
    assert full_model._data[0].normalGql == 2


def test_get_data_wrong_role_raises_exception(full_model):
    with pytest.raises(RoleDoesNotExist):
        full_model.data(full_model.index(0), 999)


def test_get_data_wrong_index_returns_None(full_model):
    assert full_model.data(full_model.index(999, 999), 256) is None


def test_child_creates_model(full_model):
    model = WithChild.Model(data=[init_dict_withChild() for _ in range(3)])
    res = model.data(full_model.index(0), model.__roles__.by_name[CHILD].num)
    assert isinstance(res, GenericModel)


def test_child_has_parent_model(full_model):
    parent_model: GenericModel[WithChild] = WithChild.Model(
        data=[init_dict_withChild() for _ in range(3)],
    )
    child_model: GenericModel[FullClass] = parent_model._data[0].child
    assert child_model.parent_model is parent_model


def test_child_model_has_parent_model(full_model):
    model = WithChild.Model(data=[init_dict_withChild() for _ in range(3)])
    res: GenericModel = model.data(full_model.index(0), model.__roles__.by_name[CHILD].num)
    assert res.parent_model is model


def test_set_data(full_model):
    full_model.setData(full_model.index(0), "VALUE", 256)
    assert full_model._data[0].normalGql == "VALUE"


def test_flags_return_editable(full_model):
    flag = full_model.flags(full_model.index(0))
    assert flag == QtCore.Qt.ItemFlag.ItemIsEditable


def test_invalid_index_returns_no_item_flag(full_model):
    flag = full_model.flags(full_model.index(25))
    assert flag == QtCore.Qt.ItemFlag.NoItemFlags


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


@patch("PySide6.QtCore.QAbstractListModel.endRemoveRows")
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


def test_custom_model(base_type):
    reached = False

    class SomeModel(base_type):
        class Model(GenericModel):
            def __init__(self, *args, **kwargs):
                nonlocal reached
                reached = True
                super().__init__(*args, **kwargs)

        a: int

    SomeModel.Model()
    assert reached
