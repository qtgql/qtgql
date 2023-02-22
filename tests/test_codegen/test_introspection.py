import pytest
from qtgql.exceptions import QtGqlException

from tests.test_codegen import schemas
from tests.test_codegen.test_py.testcases import QGQLObjectTestCase

TypeWithNoIDTestCase = QGQLObjectTestCase(
    schema=schemas.type_with_no_id.schema,
    query="""query MainQuery {users{name}}""",
    test_name="TypeWithNoIDTestCase",
)

TypeWithNullAbleIDTestCase = QGQLObjectTestCase(
    schema=schemas.type_with_nullable_id.schema,
    query="""query MainQuery {users{name}}""",
    test_name="TypeWithNullAbleIDTestCase",
)

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


def test_raises_if_no_id_on_type():
    with pytest.raises(QtGqlException):
        TypeWithNoIDTestCase.compile()


def test_raises_on_nullable_id():
    with pytest.raises(QtGqlException):
        TypeWithNullAbleIDTestCase.compile()


def test_raises_on_wrong_id_type():
    with pytest.raises(QtGqlException):
        TypeWithWrongIDTypeTestCase.compile()


def test_appends_id_field_on_query_that_wont_define_id():
    testcase = NoIdOnQueryTestCase.compile()
    assert "id" not in testcase.query
    assert "id" in testcase.query_handler._message_template.payload.query
