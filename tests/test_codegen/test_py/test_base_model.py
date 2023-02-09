import pytest
from PySide6.QtCore import QByteArray, QObject, Qt
from qtgql.codegen.py.runtime.bases import QGraphQListModel

from tests.test_codegen.test_py.test_introspection_generator import ObjectWithListOfObjectTestCase


@pytest.fixture()
def sample_model_initialized() -> QGraphQListModel:
    testcase = ObjectWithListOfObjectTestCase
    testcase.compile()
    user = testcase.gql_type
    user = user.from_dict(None, testcase.initialize_dict)
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
        sample_model_initialized.data(
            sample_model_initialized.index(0), QGraphQListModel.OBJECT_ROLE
        )
        == 2
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


class TestCurrentIndexProp:
    def test_is_0_on_init(self, qtbot, sample_model_initialized):
        assert sample_model_initialized.property("currentIndex") == 0

    def test_setter_emits(self, qtbot, sample_model_initialized):
        with qtbot.wait_signal(sample_model_initialized.currentIndexChanged):
            sample_model_initialized.set_current_index(2)
            assert sample_model_initialized.property("currentIndex") == 2


class TestCurrentObject:
    def test_getter(self, qtbot, sample_model_initialized):
        expected = QObject()
        sample_model_initialized._data.insert(0, expected)
        sample_model_initialized.set_current_index(0)
        assert sample_model_initialized.property("currentObject") is expected

    def test_setter(self, qtbot, sample_model_initialized):
        first = sample_model_initialized._data[0]
        second = QObject()
        sample_model_initialized._data.insert(1, second)
        assert sample_model_initialized.currentObject is first
        with qtbot.wait_signal(sample_model_initialized.currentIndexChanged):
            sample_model_initialized.set_current_index(1)
            assert sample_model_initialized.currentObject is second

    def test_is_first_element_when_initialized(self, sample_model_initialized):
        first = sample_model_initialized._data[0]
        assert sample_model_initialized.currentObject is first
        assert sample_model_initialized.property("currentObject") is first

    def test_is_default_when_initialized_with_no_data(self, sample_model_initialized):
        testcase = ObjectWithListOfObjectTestCase.compile()
        user = testcase.gql_type
        user = user()
        model = user.persons
        assert model.property("currentObject") is testcase.module.Person.default_instance()
