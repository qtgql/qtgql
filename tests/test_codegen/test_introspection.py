import pytest

from qtgqlcodegen.exceptions import QtGqlException
from tests.test_codegen import schemas
from tests.test_codegen.testcases import QGQLObjectTestCase
from tests.test_codegen.testcases import TypeWithNoIDTestCase
from tests.test_codegen.testcases import TypeWithNullAbleIDTestCase

TypeWithWrongIDTypeTestCase = QGQLObjectTestCase(
    schema=schemas.wrogn_id_type.schema,
    query="""query MainQuery {users{name}}""",
    test_name="TypeWithWrongIDTypeTestCase",
)

NoIdOnQueryTestCase = QGQLObjectTestCase(
    schema=schemas.object_with_scalar.schema,
    query="""
    query MainQuery {
          user {
            name
            age
            agePoint
            male
          }
        }""",
    test_name="TypeWithWrongIDTypeTestCase",
)


def test_warns_if_no_id_on_type():
    with pytest.warns(match="QtGql enforces types to have ID field"):
        with TypeWithNoIDTestCase.compile():
            ...


def test_raises_on_nullable_id():
    with pytest.warns(match="id field of type ID!"):
        with TypeWithNullAbleIDTestCase.compile():
            ...


def test_raises_on_wrong_id_type():
    with pytest.raises(QtGqlException):
        with TypeWithWrongIDTypeTestCase.compile():
            ...


def test_appends_id_field_on_query_that_wont_define_id():
    with NoIdOnQueryTestCase.compile() as testcase:
        assert "id" not in testcase.query
        assert "id" in testcase.query_handler._message_template.payload.query


class TestQtGqlQueriedObjectType:
    def test_deterministic_name(self):
        raise NotImplementedError

    def test_deterministic_fields_order(self):
        raise NotImplementedError
