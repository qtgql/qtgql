from __future__ import annotations

import os
import platform
import socket
import subprocess
import time
from pathlib import Path

import mimesis
import pytest
from attrs import define
from faker import Faker
from mimesis.locales import Locale

fake = Faker()


class PATHS:
    PROJECT_ROOT = Path(__file__).parent.parent
    QTGQL_TEST_TARGET = PROJECT_ROOT / "tests" / "build"
    ROOT_CMAKE = PROJECT_ROOT / "CMakeLists.txt"
    QTGQLCODEGEN_ROOT = PROJECT_ROOT / "qtgqlcodegen"


class PersonFactory(mimesis.Person):
    def age(self, minimum: int = 0, maximum: int = 999999) -> int:
        super().age(minimum, maximum)


class factory:
    person = PersonFactory(locale=Locale.DEFAULT)
    develop = mimesis.Development()
    numeric = mimesis.Numeric()
    text = mimesis.Text()


IS_WINDOWS = platform.system() == "Windows"
IS_GITHUB_ACTION = os.environ.get("CI", False)


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
    address = f"://localhost:{port}/graphql"
    time.sleep(5)
    assert not p.poll(), p.stdout.read().decode("utf-8")
    ms = MiniServer(process=p, address=address, port=port)
    yield ms
    if p.poll() is None:
        p.terminate()
