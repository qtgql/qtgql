import pytest
from qtgqlcodegen.core.exceptions import QtGqlException
from tests.test_codegen import schemas
from tests.test_codegen.testcases import QtGqlTestCase

TypeWithWrongIDTypeTestCase = QtGqlTestCase(
    test_name="TypeWithWrongIDTypeTestCase",
    schema=schemas.wrogn_id_type.schema,
    operations="""query MainQuery {users{name}}""",
    is_virtual_test=True,
)


def test_raises_on_wrong_id_type():
    with pytest.raises(QtGqlException):
        with TypeWithWrongIDTypeTestCase.virtual_generate():
            ...
