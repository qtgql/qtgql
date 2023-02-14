import pytest
from qtgql.codegen.py.runtime.environment import ENV_MAP, QtGqlEnvironment
from qtgql.codegen.py.runtime.queryhandler import BaseQueryHandler
from qtgql.gqltransport.client import GqlWsTransportClient

from tests.test_codegen.test_py.testcases import ScalarsTestCase


def test_query_handler_from_qml(qmlbot, mini_server, testcase):
    testcase = ScalarsTestCase.compile(mini_server.address).load_qml(qmlbot)
    rq = testcase.qml_queryhandler
    qmlbot.bot.wait_until(lambda: bool(rq._data))
    assert isinstance(rq._data, testcase.gql_type)


def test_on_completed_emits(qmlbot, mini_server):
    testcase = ScalarsTestCase.compile(mini_server.address).load_qml(qmlbot)
    rq = testcase.qml_queryhandler
    with qmlbot.bot.wait_signal(rq.completedChanged):
        qmlbot.bot.wait_until(lambda: bool(rq._data))


@pytest.fixture()
def pseudo_environment():
    ENV_MAP["DEFAULT"] = QtGqlEnvironment(GqlWsTransportClient(url=""))
    yield
    ENV_MAP.pop("DEFAULT")


def test_is_singleton(pseudo_environment):
    class Foo(BaseQueryHandler):
        ...

    assert Foo() is Foo()


def test_fetch_when_first_consumers_connects_to_dataChanged():
    raise NotImplementedError
