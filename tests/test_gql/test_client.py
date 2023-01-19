import pytest
from PySide6.QtNetwork import QAbstractSocket
from qtgql.gqlcore.client import PROTOCOL, GqlWsTransportClient, SubscribeResponseMessage
from qtgql.gqlcore.gqlcore import QueryPayload

from tests.test_gql.fixtures import get_subscription_str

pytest_plugins = ("tests.test_gql.fixtures",)


def test_get_operation_name():
    payload = QueryPayload(query=get_subscription_str(operation_name="TestOperationName"))
    assert payload.operationName == "TestOperationName"


def test_connection_init(qtbot, mini_server):
    client = GqlWsTransportClient(ping_timeout=20000, url=mini_server.address)
    assert not client._connection_ack
    qtbot.wait_until(lambda: client._connection_ack)


def test_connection_pong(qtbot, mini_server):
    caught = False

    class CatchPong(GqlWsTransportClient):
        def _on_gql_pong(self) -> None:
            nonlocal caught
            caught = True

    client = CatchPong(ping_timeout=20000, url=mini_server.address)
    qtbot.wait_until(client.isValid)
    assert caught


def test_subscribe_data(qtbot, mini_server, default_handler):
    target = 0

    class CatchNext(GqlWsTransportClient):
        def _on_gql_next(self, message: SubscribeResponseMessage):
            assert message.type == PROTOCOL.NEXT
            assert message.payload
            nonlocal target
            target = message.payload["data"]["count"]

    client = CatchNext(ping_timeout=10000000, url=mini_server.address)
    qtbot.wait(100)
    client.subscribe(default_handler)

    def cond():
        assert target == 9

    qtbot.wait_until(cond)


def test_subscribe_compete_protocol(qtbot, mini_server, default_handler):
    reached = False

    class CatchComplete(GqlWsTransportClient):
        def _on_gql_complete(self, message: SubscribeResponseMessage):
            nonlocal reached
            reached = True
            assert message.type == PROTOCOL.COMPLETE
            assert self.isValid()
            super()._on_gql_complete(message)
            assert self.isValid()

    client = CatchComplete(ping_timeout=90000, url=mini_server.address)
    qtbot.wait(500)
    client.subscribe(default_handler)
    qtbot.wait(300)
    assert reached


def test_ping_timeout_close_connection(qtbot, mini_server):
    class NoPongClient(GqlWsTransportClient):
        def _on_gql_pong(self) -> None:
            pass

    client = NoPongClient(ping_timeout=500, url=mini_server.address)
    qtbot.wait(100)
    assert client.isValid()
    qtbot.wait(500)
    assert not client.isValid()


def test_gql_is_valido_not_valid_if_no_ack(qtbot, mini_server):
    class NoAckClient(GqlWsTransportClient):
        def _on_gql_ack(self) -> None:
            ...

    client = NoAckClient(ping_timeout=300, url=mini_server.address)
    qtbot.wait(100)
    assert not client.gql_is_valid()
    assert client.isValid()


def test_not_gql_is_valid_if_not_isValid(qtbot, default_client):
    assert default_client.isValid()
    assert default_client.gql_is_valid()
    req = default_client.request()
    default_client.close()
    assert not default_client.isValid()
    assert not default_client.gql_is_valid()
    default_client._init_connection(req)
    qtbot.wait(300)
    assert default_client.isValid()
    assert default_client.gql_is_valid()


@pytest.fixture
def auto_reconnect_client(qtbot, mini_server):
    client = GqlWsTransportClient(
        url=mini_server.address, auto_reconnect=True, reconnect_timeout=100
    )
    qtbot.wait_until(client.gql_is_valid)
    return client


def test_wont_reconnect_if_reconnect_is_false(qtbot, mini_server):
    client = GqlWsTransportClient(
        url=mini_server.address, auto_reconnect=False, reconnect_timeout=100
    )
    qtbot.wait_until(client.gql_is_valid)
    client.close()
    assert not client.isValid()
    qtbot.wait(100)
    assert not client.isValid()


def test_reconnects_on_disconnected_if_auto_reconnect_is_True(qtbot, auto_reconnect_client):
    auto_reconnect_client.close()
    assert not auto_reconnect_client.isValid()
    qtbot.wait_until(auto_reconnect_client.gql_is_valid)


def test_reconnects_on_error_if_not_valid(qtbot, auto_reconnect_client):
    temp = auto_reconnect_client.isValid
    auto_reconnect_client.isValid = lambda: False
    auto_reconnect_client.on_error(QAbstractSocket.SocketError.NetworkError)
    auto_reconnect_client.isValid = temp
    qtbot.wait_until(auto_reconnect_client.isValid)
    qtbot.wait_until(auto_reconnect_client.isValid)


def test_stops_reconnect_timer_on_connected(qtbot, mini_server):
    client = GqlWsTransportClient(
        url=mini_server.address, auto_reconnect=True, reconnect_timeout=100
    )
    qtbot.wait_until(client.gql_is_valid)
    client.close()
    assert not client.isValid()
    qtbot.wait_until(client.gql_is_valid)
    assert not client.reconnect_timer.isActive()
