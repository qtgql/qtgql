from __future__ import annotations

from PySide6.QtCore import QObject


class BaseQGraphQLObject(QObject):
    def __init__(self, parent: QObject | None = None):
        return super().__init__(parent)

    @classmethod
    def from_dict(cls, data: dict) -> BaseQGraphQLObject:
        raise NotImplementedError
