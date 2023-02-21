import pytest
from qtgql.exceptions import QtGqlException

from tests.test_codegen.test_py.testcases import (
    TypeWithNoIDTestCase,
    TypeWithNullAbleIDTestCase,
    TypeWithWrongIDTypeTestCase,
)


def test_raises_if_no_id_on_type():
    with pytest.raises(QtGqlException):
        TypeWithNoIDTestCase.compile()


def test_raises_on_nullable_id():
    with pytest.raises(QtGqlException):
        TypeWithNullAbleIDTestCase.compile()


def test_raises_on_wrong_id_type():
    with pytest.raises(QtGqlException):
        TypeWithWrongIDTypeTestCase.compile()
