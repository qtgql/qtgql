from enum import Enum
from typing import Any, ClassVar, Generic, Optional, TypeVar

from PySide6.QtCore import QObject, Signal

from qtgql import qproperty, slot
from qtgql.codegen.py.runtime.environment import get_default_env
from qtgql.gqltransport.client import GqlClientMessage

T_QObject = TypeVar("T_QObject", bound=QObject)


class SignalName(Enum):
    Data, Completed, Error = range(3)


class BaseQueryHandler(Generic[T_QObject], QObject):
    """Each handler will be exposed to QML and."""

    operationName: ClassVar[str]
    _message_template: ClassVar[GqlClientMessage]

    graphqlChanged = Signal()
    dataChanged = Signal()
    completedChanged = Signal()
    errorChanged = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._query = None
        self._completed = bool
        self._data: Optional[T_QObject] = None
        self.environment = get_default_env()
        self.setObjectName(self.__class__.__name__)

    @slot
    def set_graphql(self, query: str) -> None:
        self._query = query
        if not self._data:
            self.fetch()

    @property
    def message(self) -> GqlClientMessage:
        assert self._query
        self._message_template.payload.query = self._query
        return self._message_template

    @qproperty(str, fset=set_graphql, notify=graphqlChanged)
    def graphql(self):
        return self._query

    @qproperty(QObject, notify=dataChanged)
    def data(self) -> Optional[QObject]:
        return self._data

    @qproperty(bool, notify=completedChanged)
    def completed(self):
        return self._completed

    def fetch(self) -> None:
        self.environment.client.query(self)

    def on_data(self, message: dict) -> None:
        raise NotImplementedError

    def on_completed(self) -> None:
        self._completed = True
        self.completedChanged.emit()

    def on_error(self, message: list[dict[str, Any]]) -> None:
        raise NotImplementedError
