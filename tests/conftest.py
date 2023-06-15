from __future__ import annotations

import hashlib
import os
import platform
import socket
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING

import mimesis
import pytest
from attrs import define
from faker import Faker
from mimesis.locales import Locale

if TYPE_CHECKING:
    from strawberry import Schema

fake = Faker()


class PATHS:
    PROJECT_ROOT = Path(__file__).parent.parent
    QTGQL_TEST_TARGET = PROJECT_ROOT / "tests" / "build"


class factory:
    person = mimesis.Person(locale=Locale.DEFAULT)
    develop = mimesis.Development()
    numeric = mimesis.Numeric()
    text = mimesis.Text()


IS_WINDOWS = platform.system() == "Windows"
IS_GITHUB_ACTION = os.environ.get("CI", False)


def hash_schema(schema: Schema) -> int:
    return int(hashlib.sha256(str(schema).encode("utf-8")).hexdigest(), 16) % 10**8


@define
class MiniServer:
    process: subprocess.Popen
    address: str
    port: str


@pytest.fixture(scope="session")
def schemas_server() -> MiniServer:
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
            "tests.scripts.tests_server:init_func",
        ],
        env=os.environ.copy(),
        cwd=Path(__file__).parent.parent,
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
