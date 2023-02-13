from typing import Optional

from PySide6.QtCore import QObject

QML_IMPORT_NAME = "QtGql"
QML_IMPORT_MAJOR_VERSION = 1


class UseQuery(QObject):
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
