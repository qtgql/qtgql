import pytest

from qtgqlcodegen.exceptions import QtGqlException
from tests.test_codegen import schemas
from tests.test_codegen.testcases import QGQLObjectTestCase
from tests.test_codegen.testcases import TypeWithNoIDTestCase
from tests.test_codegen.testcases import TypeWithNullAbleIDTestCase

TypeWithWrongIDTypeTestCase = QGQLObjectTestCase(
    schema=schemas.wrogn_id_type.schema,
    operations="""query MainQuery {users{name}}""",
    test_name="TypeWithWrongIDTypeTestCase",
)


@pytest.mark.skip(reason="These tests are yet to be generated")
def test_warns_if_no_id_on_type():
    with pytest.warns(match="QtGql enforces types to have ID field"):
        with TypeWithNoIDTestCase.compile():
            ...


@pytest.mark.skip(reason="These tests are yet to be generated")
def test_raises_on_nullable_id():
    with pytest.warns(match="id field of type ID!"):
        with TypeWithNullAbleIDTestCase.compile():
            ...


@pytest.mark.skip(reason="These tests are yet to be generated")
def test_raises_on_wrong_id_type():
    with pytest.raises(QtGqlException):
        with TypeWithWrongIDTypeTestCase.compile():
            ...
