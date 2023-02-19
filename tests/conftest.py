import hashlib
import os
import socket
import subprocess
import tempfile
import time
from pathlib import Path
from typing import TypeVar

import pytest
from attr import field
from attrs import define
from faker import Faker
from PySide6.QtCore import QUrl
from PySide6.QtQuick import QQuickItem, QQuickView
from pytestqt.qtbot import QtBot
from strawberry import Schema

fake = Faker()


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
            "tests.mini_gql_server:init_func",
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


T = TypeVar("T")


@define(slots=False)
class QmlBot:
    bot: QtBot
    qquickiew: QQuickView = field(factory=QQuickView)

    @property
    def engine(self):
        return self.qquickiew.engine()

    def load(self, path: Path) -> QQuickItem:
        self.engine.clearComponentCache()
        self.qquickiew.setSource(QUrl(path.as_posix()))
        if errors := self.qquickiew.errors():
            raise RuntimeError("errors in view", errors)
        self.qquickiew.show()
        return self.find("rootObject")

    def loads(self, content: str) -> QQuickItem:
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "TestComp.qml"
            target.write_text(content)
            return self.load(target)

    def find(self, objectname: str, type: T = QQuickItem) -> T:
        return self.qquickiew.findChild(type, objectname)

    def cleanup(self):
        self.qquickiew.close()
        self.qquickiew.deleteLater()


@pytest.fixture()
def qmlbot(qtbot):
    bot = QmlBot(qtbot)
    yield bot


def hash_schema(schema: Schema) -> int:
    return int(hashlib.sha256(str(schema).encode("utf-8")).hexdigest(), 16) % 10**8
