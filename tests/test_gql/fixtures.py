from dataclasses import dataclass
from pathlib import Path
import socket
import subprocess
import time

import pytest

from qtier.gql.client import GqlClientMessage, GqlWsTransportClient, HandlerProto


@dataclass
class MiniServer:
    process: subprocess.Popen
    address: str
    port: str


@staticmethod
def get_subscription_str(operation_name="", target: int = 10, raise_on_5=False) -> str:
    return "subscription {} {{ count(target: {}, raiseOn5: {}) }}".format(
        operation_name,
        target,
        "true" if raise_on_5 else "false",
    )


@pytest.fixture(scope="session")
def mini_server() -> MiniServer:
    sock = socket.socket()
    sock.bind(("", 0))
    port = str(sock.getsockname()[1])
    sock.close()
    p = subprocess.Popen(
        args=[
            "poetry",
            "run",
            "python",
            "-m",
            "aiohttp.web",
            "-H",
            "localhost",
            f"-P {port}",
            "mini_gql_server:init_func",
        ],
        cwd=Path(__file__).parent,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    address = f"ws://localhost:{port}/graphql"
    time.sleep(5)
    assert not p.poll(), p.stdout.read().decode("utf-8")
    ms = MiniServer(process=p, address=address, port=port)
    yield ms
    if p.poll() is None:
        p.terminate()


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
