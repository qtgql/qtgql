import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import pytest
from faker import Faker

fake = Faker()


@dataclass
class MiniServer:
    process: subprocess.Popen
    address: str
    port: str


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
            "tests.mini_gql_server:init_func",
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
