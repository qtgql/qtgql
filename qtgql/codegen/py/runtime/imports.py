from PySide6.QtCore import QObject
from PySide6.QtQml import QmlElement, QmlSingleton

from qtgql import slot

QML_IMPORT_NAME = "QtGql"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
@QmlSingleton
class Funcs(QObject):
    @slot
    def graphql(self, query: str) -> str:
        return query
