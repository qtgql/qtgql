import platform

import pytest
from qtgql.gqltransport.client import PROTOCOL, GqlWsTransportClient, SubscribeResponseMessage

from tests.test_gqltransport.conftest import PseudoHandler, get_subscription_str


def test_generates_has_query_map_with_id_and_receivers(default_client):
    subscriber_1 = PseudoHandler(get_subscription_str())
    subscriber_2 = PseudoHandler(get_subscription_str())
    assert subscriber_1.message.id != subscriber_2.message.id
    default_client.subscribe(subscriber_1)
    default_client.subscribe(subscriber_2)
    assert len(default_client.handlers.keys()) == 2


def test_subscriber_called_with_on_gql_next(qtbot, default_client):
    client = default_client
    subscriber_1 = PseudoHandler(get_subscription_str(target=5))
    subscriber_2 = PseudoHandler(get_subscription_str(target=2))
    assert subscriber_1.message.id != subscriber_2.message.id
    client.subscribe(subscriber_1)
    client.subscribe(subscriber_2)
    qtbot.wait(500)
    assert subscriber_1.data["count"] == 4
    assert subscriber_2.data["count"] == 1


def test_subscriber_called_with_on_gql_complete(qtbot, default_client, default_handler):
    assert not default_handler.completed
    default_client.subscribe(default_handler)
    qtbot.wait_until(lambda: default_handler.completed)


def test_subscribe_complete_pops_subscriber_with_this_id(qtbot, schemas_server, default_handler):
    subscriber_id = None

    class CatchComplete(GqlWsTransportClient):
        def _on_gql_complete(self, message: SubscribeResponseMessage):
            nonlocal subscriber_id
            subscriber_id = message.id
            assert message.type == PROTOCOL.COMPLETE
            assert self.isValid()
            assert self.handlers[message.id]
            super()._on_gql_complete(message)
            assert self.isValid()
            assert not self.handlers.get(message.id, None)

    client = CatchComplete(ping_timeout=90000, url=schemas_server.address)
    qtbot.wait(500)
    client.subscribe(default_handler)

    def cond():
        assert subscriber_id == default_handler.message.id

    qtbot.wait_until(cond)


@pytest.mark.skipif(
    "Windows" in platform.platform(), reason="for wome reason the server will die here on windows"
)
def test_gql_error_sends_error_to_subscriber(qtbot, default_client, default_handler):
    error_subscriber = PseudoHandler(get_subscription_str(raise_on_5=True))
    default_client.subscribe(default_handler)
    default_client.subscribe(error_subscriber)
    qtbot.wait(500)
    assert error_subscriber.data["count"] == 4
    assert error_subscriber.error == [{"message": "Test Gql Error"}]
    assert default_handler.data["count"] == 9


def test_when_not_valid_pends_a_message_and_sends_on_connect(
    qtbot, schemas_server, default_handler
):
    client = GqlWsTransportClient(url=schemas_server.address)
    qtbot.wait(300)
    assert client.isValid()
    req = client.request()
    client.close()
    assert not client.isValid()
    client.subscribe(default_handler)
    assert not client.isValid()
    client._init_connection(req)

    def cond():
        assert client.isValid()
        assert default_handler.data["count"]

    qtbot.wait_until(cond)


def test_mutations(qtbot, default_client):
    subscriber = PseudoHandler("mutation TestMutation{pseudoMutation}")
    default_client.query(subscriber)
    qtbot.wait(300)
    assert subscriber.data == {"pseudoMutation": True}

    def cond():
        assert not default_client.handlers

    qtbot.wait_until(cond)


def test_query(qtbot, default_client):
    subscriber = PseudoHandler("query TestQuery{hello}")
    default_client.query(subscriber)
    qtbot.wait(300)
    assert subscriber.data == {"hello": "world"}
    qtbot.wait(300)
    assert not default_client.handlers


def test_header_authentications_headers(qtbot, schemas_server):
    subscriber = PseudoHandler("query MyQuery {isAuthenticated}")
    token = "FakeToken"
    authorized_client = GqlWsTransportClient(
        url=schemas_server.address, headers={b"Authorization": token.encode()}
    )
    authorized_client.query(subscriber)

    def cond():
        assert subscriber.completed

    qtbot.wait_until(cond, timeout=2000)
    assert subscriber.data == {"isAuthenticated": token}
    assert not authorized_client.handlers
