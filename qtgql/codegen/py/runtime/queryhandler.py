from typing import Any, ClassVar, Generic, Optional, TypeVar

from PySide6.QtCore import QObject, Signal

from qtgql.codegen.py.runtime.environment import get_gql_env
from qtgql.exceptions import QtGqlException
from qtgql.gqltransport.client import GqlClientMessage
from qtgql.tools import qproperty, slot

T_QObject = TypeVar("T_QObject", bound=QObject)


class BaseQueryHandler(Generic[T_QObject], QObject):
    """Each handler will be exposed to QML and."""

    __instance__: "Optional[ClassVar[BaseQueryHandler]]" = None
    ENV_NAME: ClassVar[str]
    operationName: ClassVar[str]
    _message_template: ClassVar[GqlClientMessage]

    graphqlChanged = Signal()
    dataChanged = Signal()
    completedChanged = Signal()
    errorChanged = Signal()

    signalNames = ("graphqlChanged", "dataChanged", "completedChanged", "errorChanged")

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        name = self.__class__.__name__
        if self.__instance__:
            raise QtGqlException("Query handlers should be instantiated only once")
        self.__instance__ = self
        self._query: str = ""
        self._completed: bool = False
        self._data: Optional[T_QObject] = None
        self.environment = get_gql_env(self.ENV_NAME)
        self.environment.add_query_handler(self)
        self.setObjectName(name)
        self._consumers_count: int = 0

    @property
    def consumers(self):
        return self._consumers_count

    @consumers.setter
    def consumers(self, v: int):
        self._consumers_count = v

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
        self.environment.client.execute(self)  # type: ignore

    def on_data(self, message: dict) -> None:  # pragma: no cover
        # real is on derived class.
        raise NotImplementedError

    def on_completed(self) -> None:
        self._completed = True
        self.completedChanged.emit()

    def on_error(self, message: list[dict[str, Any]]) -> None:  # pragma: no cover
        # This (unlike `on_data` is not implemented for real)
        raise NotImplementedError(message)

    def connectNotify(self, signal) -> None:
        if signal.name().toStdString() == "dataChanged":
            self.consumers += 1
        super().connectNotify(signal)
