import pytest
from PySide6.QtCore import QByteArray, Qt
from qtgql.codegen.introspection import SchemaEvaluator
from qtgql.codegen.py.bases import BaseModel, _BaseQGraphQLObject

from tests.test_codegen.conftest import get_introspection_for
from tests.test_codegen.schemas import object_with_list_of_object
from tests.test_codegen.test_py.test_introspection_generator import TestObjectWithListOfObject


@pytest.fixture()
def sample_model_initialized(tmp_mod) -> BaseModel:
    schema = object_with_list_of_object.schema
    introspection = get_introspection_for(schema)
    res = SchemaEvaluator(introspection)
    generated = res.generate()
    compiled = compile(generated, "schema", "exec")
    exec(compiled, tmp_mod.__dict__)
    User: _BaseQGraphQLObject = tmp_mod.User
    user = User.from_dict(None, TestObjectWithListOfObject.initialize_dict)
    return user.persons


def test_returns_object_role(sample_model_initialized):
    assert sample_model_initialized.roleNames() == {
        Qt.ItemDataRole.UserRole + 1: QByteArray("object")
    }


def test_row_count(sample_model_initialized):
    count = len(sample_model_initialized._data)
    assert count == sample_model_initialized.rowCount()


def test_returns_data(sample_model_initialized):
    sample_model_initialized._data[0] = 2
    assert (
        sample_model_initialized.data(sample_model_initialized.index(0), BaseModel.OBJECT_ROLE) == 2
    )


def test_pop(qtbot, sample_model_initialized):
    original_data = sample_model_initialized._data.copy()
    with qtbot.wait_signal(sample_model_initialized.rowsAboutToBeRemoved):
        sample_model_initialized.pop(0)
    assert original_data != sample_model_initialized._data
    original_data.pop(0)
    assert original_data == sample_model_initialized._data


def test_append(qtbot, sample_model_initialized):
    with qtbot.wait_signal(sample_model_initialized.rowsAboutToBeInserted):
        sample_model_initialized.append("foo")
    assert "foo" in sample_model_initialized._data
