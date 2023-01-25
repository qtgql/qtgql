import pytest
from qtgql.gqltransport.client import GqlClientMessage, GqlWsTransportClient, HandlerProto


@staticmethod
def get_subscription_str(operation_name="", target: int = 10, raise_on_5=False) -> str:
    return "subscription {} {{ count(target: {}, raiseOn5: {}) }}".format(
        operation_name,
        target,
        "true" if raise_on_5 else "false",
    )


@pytest.fixture
def default_handler() -> "PseudoHandler":
    return PseudoHandler()


@pytest.fixture
def default_client(qtbot, mini_server) -> GqlWsTransportClient:
    client = GqlWsTransportClient(url=mini_server.address)
    qtbot.wait_until(client.gql_is_valid)
    yield client
    assert client.gql_is_valid()
    client.close()


class PseudoHandler(HandlerProto):
    def __init__(self, query: str = None):
        self.message = GqlClientMessage.from_query(query=query or get_subscription_str())
        self.data = None
        self.error = None
        self.completed = False

    def on_data(self, res: dict) -> None:
        self.data = res

    def on_error(self, message) -> None:
        self.error = message

    def on_completed(self) -> None:
        self.completed = True
