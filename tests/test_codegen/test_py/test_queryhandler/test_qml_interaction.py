from textwrap import dedent

from tests.test_codegen.test_py.testcases import ScalarsTestCase


def test_on_completed_emits(qmlbot, schemas_server):
    testcase = ScalarsTestCase.compile(schemas_server.address).load_qml(qmlbot)
    with qmlbot.bot.wait_signal(testcase.qml_queryhandler.completedChanged):
        ...
    assert testcase.qml_queryhandler.property("completed") is True


def test_data_fetched(qmlbot, schemas_server):
    testcase = ScalarsTestCase.compile(schemas_server.address).load_qml(qmlbot)
    with qmlbot.bot.wait_signal(testcase.qml_queryhandler.dataChanged):
        ...
    assert isinstance(testcase.qml_queryhandler.property("data"), testcase.gql_type)


def test_graphql_prop(qmlbot, schemas_server):
    testcase = ScalarsTestCase.compile(schemas_server.address).load_qml(qmlbot)
    assert testcase.query in dedent(testcase.qml_queryhandler.property("graphql"))
