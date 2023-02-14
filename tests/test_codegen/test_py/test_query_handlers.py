from tests.test_codegen.test_py.testcases import ScalarsTestCase


def test_query_handler_from_qml(qmlbot, mini_server):
    testcase = ScalarsTestCase.compile(mini_server.address).load_qml(qmlbot)
    rq = testcase.qml_queryhandler
    qmlbot.bot.wait_until(lambda: bool(rq._data))
    assert isinstance(rq._data, testcase.gql_type)


def test_on_completed_emits(qmlbot, mini_server):
    testcase = ScalarsTestCase.compile(mini_server.address).load_qml(qmlbot)
    rq = testcase.qml_queryhandler
    with qmlbot.bot.wait_signal(rq.completedChanged):
        qmlbot.bot.wait_until(lambda: bool(rq._data))
