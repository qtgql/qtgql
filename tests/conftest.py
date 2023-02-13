import hashlib
import socket
import subprocess
import time
from pathlib import Path
from typing import TypeVar

import pytest
from attr import field
from attrs import define
from faker import Faker
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent
from PySide6.QtQuick import QQuickItem
from pytestqt.qtbot import QtBot
from strawberry import Schema

fake = Faker()


@define
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


T = TypeVar("T")


@define(slots=False)
class QmlBot:
    bot: QtBot
    engine: QQmlApplicationEngine = field(factory=QQmlApplicationEngine)

    def __attrs_post_init__(self):
        main = Path(__file__).parent / "qmltester.qml"
        self.engine.load(main.resolve(True))

    @property
    def _loader(self) -> QQuickItem:
        self.root = self.engine.rootObjects()[0]
        return self.root.findChild(QQuickItem, "contentloader")

    def load(self, path: Path) -> QQuickItem:
        self.bot.wait(100)
        self._loader.setProperty("source", str(path.resolve(True)))
        return self._loader.property("item")

    def loads(self, content: str) -> QQuickItem:
        self.comp = QQmlComponent(self.engine)
        self.comp.setData(content.encode("utf-8"), QUrl("./"))
        self._loader.setProperty("source", "")
        self._loader.setProperty("sourceComponent", self.comp)
        return self._loader.property("item")

    def loads_many(self, components: dict[str, str]):
        for name, content in components.items():
            comp = QQmlComponent(self.engine)
            comp.setData(content.encode("utf-8"), QUrl("./"))

        self.loads(components["main.qml"])

    def find(self, objectname: str, type: T = QQuickItem) -> T:
        return self._loader.findChild(type, objectname)


@pytest.fixture()
def qmlbot(qtbot):
    return QmlBot(qtbot)


def hash_schema(schema: Schema) -> int:
    return int(hashlib.sha256(str(schema).encode("utf-8")).hexdigest(), 16) % 10**8
