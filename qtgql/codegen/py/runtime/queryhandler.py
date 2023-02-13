from enum import Enum
from typing import Generic, Optional, TypeVar

from PySide6.QtCore import QObject, Signal

from qtgql import qproperty, slot
from qtgql.codegen.py.runtime.environment import QtGqlEnvironment, get_default_env
from qtgql.gqltransport.client import GqlClientMessage

T = TypeVar("T", bound=QObject)


class SignalName(Enum):
    Data, Completed, Error = range(3)


class BaseQueryHandler(Generic[T], QObject):
    """Each handler will be exposed to QML and."""

    query: str
    environment: QtGqlEnvironment

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.consumers: list[UseQuery] = []
        self.message = GqlClientMessage.from_query(self.query)
        self._data: Optional[T] = None
        self.query_id = hash(self.query)

    @property
    def data(self):
        return self._data

    def register_consumer(self, consumer: "UseQuery") -> None:
        self.consumers.append(consumer)

    def remove_consumer(self, consumer: "UseQuery") -> None:
        self.consumers.remove(consumer)

    def notify_consumers(self, sig: SignalName):
        for consumer in self.consumers:
            if sig is SignalName.Data:
                consumer.dataChanged.emit()
            elif sig is SignalName.Completed:
                consumer.completedChanged.emit()
            else:
                raise NotImplementedError

    def fetch(self) -> None:
        self.environment.client.query(self)

    def __hash__(self):
        return self.query_id


class UseQuery(QObject):
    queryChanged = Signal()
    dataChanged = Signal()
    completedChanged = Signal()
    errorChanged = Signal()

    def __init__(self, parent: Optional[QObject] = None):
        super.__init__(parent)
        self._query: str = ""
        self.environment = get_default_env()
        self._handler: Optional[BaseQueryHandler] = None

    @slot
    def set_query(self, query: str) -> None:
        assert not self._query
        self._query = query
        self._handler = self.environment.get_handler_by_query(hash(query))
        self._handler.register_consumer(self)

    @qproperty(str, fset=set_query, notify=queryChanged)
    def query(self):
        return self._query

    def deleteLater(self) -> None:
        self._handler.remove_consumer(self)

    @qproperty(QObject, notify=dataChanged)
    def data(self) -> QObject:
        if self._handler:
            return self._handler.data
