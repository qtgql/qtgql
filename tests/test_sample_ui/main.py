import glob
import os
import sys
from pathlib import Path
from typing import Optional

from PySide6 import QtCore, QtGui, QtQml, QtQuick
from PySide6.QtCore import QObject, Signal
from PySide6.QtQml import QQmlApplicationEngine
from qtgql.codegen.py.compiler.config import QtGqlConfig
from qtgql.gqltransport.client import GqlClientMessage, GqlWsTransportClient, HandlerProto
from qtgql.tools import slot

from tests.mini_gql_server import schema

try:
    from tests.test_sample_ui.__temp import Query
except ImportError:
    Query = None
from tests.test_sample_ui.qml.icons import ICONS

DEV = not os.environ.get("IS_GITHUB_ACTION", False)


class EntryPoint(QObject):
    if DEV:
        qmlFileChanged = Signal()

    class AppleHandler(HandlerProto):
        message = GqlClientMessage.from_query(
            """
            query MyQuery {
              apples {
                color
                owner
                size
                worms {
                  family
                  name
                  size
                }
              }
            }
            """
        )

        def __init__(self, app: "EntryPoint"):
            self.app = app

        def on_data(self, message: dict) -> None:
            self.app.set_root_query(Query.from_dict(None, message))

        def on_error(self, message: dict) -> None:
            raise Exception(message)

        def on_completed(self) -> None:
            ...

    def __init__(self, parent=None):
        super().__init__(parent)
        main_qml = Path(__file__).parent / "qml" / "main.qml"
        QtGui.QFontDatabase.addApplicationFont(
            str(main_qml.parent / "materialdesignicons-webfont.ttf")
        )
        self.qml_engine = QQmlApplicationEngine()
        self.gql_client = GqlWsTransportClient(url="ws://localhost:8080/graphql")
        self.apple_query_handler = self.AppleHandler(self)
        self.gql_client.execute(self.apple_query_handler)
        self._root_query: Optional[Query] = None
        QtQml.qmlRegisterSingletonInstance(EntryPoint, "com.props", 1, 0, "EntryPoint", self)  # type: ignore
        # for some reason the app won't initialize without this event processing here.
        QtCore.QEventLoop().processEvents(QtCore.QEventLoop.ProcessEventsFlag.AllEvents, 1000)
        self.qml_engine.load(str(main_qml.resolve()))

        if DEV:
            qml_files = []
            for file in glob.iglob("**/*.qml", root_dir=main_qml.parent, recursive=True):
                qml_files.append(str((main_qml.parent / file).resolve()))
            self.file_watcher = QtCore.QFileSystemWatcher(self)
            self.file_watcher.addPaths(qml_files)
            self.file_watcher.fileChanged.connect(self.on_qml_file_changed)  # type: ignore

    rootQueryChanged = Signal()

    def set_root_query(self, v: Query):
        self._root_query = v
        self.rootQueryChanged.emit()

    @QtCore.Property(QtCore.QObject, notify=rootQueryChanged)
    def rootQuery(self) -> Optional[Query]:
        return self._root_query

    @QtCore.Property("QVariant", constant=True)
    def icons(self) -> dict:
        return ICONS

    if DEV:  # pragma: no cover

        @slot
        def on_qml_file_changed(self) -> None:
            self.qml_engine.clearComponentCache()
            window: QtQuick.QQuickWindow
            for window in self.qml_engine.rootObjects():  # type: ignore
                loader: QtQuick.QQuickItem = window.findChild(QtQuick.QQuickItem, "debug_loader")  # type: ignore
                QtCore.QEventLoop().processEvents(
                    QtCore.QEventLoop.ProcessEventsFlag.AllEvents, 1000
                )
                prev = loader.property("source")
                loader.setProperty("source", "")
                loader.setProperty("source", prev)

    def deleteLater(self) -> None:
        # Deleting the engine before it goes out of scope is required to make sure
        # all child QML instances are destroyed in the correct order.
        del self.qml_engine
        super().deleteLater()


graphql_dir = Path(__file__).parent / "graphql"
(graphql_dir / "schema.graphql").write_text(str(schema))
qtgqlconfig = QtGqlConfig(graphql_dir=graphql_dir)


def main():  # pragma: no cover
    app = QtGui.QGuiApplication(sys.argv)
    EntryPoint()
    ret = app.exec()
    sys.exit(ret)


if __name__ == "__main__":
    #
    # with open(Path(__file__).parent / '__temp.py', 'w') as fh:

    main()
