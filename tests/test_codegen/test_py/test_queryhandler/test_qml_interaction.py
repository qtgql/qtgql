from tests.test_codegen.test_py.testcases import ScalarsTestCase


def test_data_fetched(qmlbot, schemas_server):
    testcase = ScalarsTestCase.compile(schemas_server.address).load_qml(qmlbot)
    with qmlbot.bot.wait_signal(testcase.query_handler.dataChanged):
        ...
    assert isinstance(testcase.query_handler.property("data"), testcase.gql_type)


def test_operationName_prop(qmlbot, schemas_server):
    testcase = ScalarsTestCase.compile(schemas_server.address)
    item = qmlbot.loads(testcase.qml_file)
    assert item.property("operationName") == testcase.query_operationName


def test_on_completed_emits(qmlbot, schemas_server):
    testcase = ScalarsTestCase.compile(schemas_server.address).load_qml(qmlbot)
    with qmlbot.bot.wait_signal(testcase.query_handler.completedChanged):
        ...
    assert testcase.query_handler.property("completed") is True


def test_consumer_deleted_decrease_consumers_count(qmlbot):
    testcase = ScalarsTestCase.compile("").load_qml(qmlbot)
    handler = testcase.query_handler
    qmlbot.bot.wait_until(lambda: bool(handler._consumers_count))
    assert handler._consumers_count
    qmlbot.cleanup()
    qmlbot.bot.wait_until(lambda: not handler._consumers_count)
    assert not handler._consumers_count
