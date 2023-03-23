from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    NamedTuple,
    Optional,
    TypeVar,
)

from PySide6.QtCore import QObject, Signal
from PySide6.QtQuick import QQuickItem

from qtgql.codegen.py.runtime.environment import get_gql_env
from qtgql.tools import qproperty, slot

if TYPE_CHECKING:
    from qtgql.gqltransport.client import GqlClientMessage

T_QObject = TypeVar("T_QObject", bound=QObject)


class SelectionConfig(NamedTuple):
    selections: Dict[str, Optional[SelectionConfig]] = {}
    choices: Dict[str, SelectionConfig] = {}


class OperationMetaData(NamedTuple):
    operation_name: str
    selections: Optional[SelectionConfig] = None


T = TypeVar("T")


class BaseOperationHandler(QObject, Generic[T]):
    # class-vars
    ENV_NAME: ClassVar[str]
    OPERATION_METADATA: ClassVar[OperationMetaData]
    _message_template: ClassVar[GqlClientMessage]

    # signals
    dataChanged = Signal()
    completedChanged = Signal()
    operationOnFlightChanged = Signal()
    error = Signal(list)

    setVariables: Callable  # implementation by jinja.

    def __init__(self, parent: Optional[QObject]):
        super().__init__(parent)
        name = self.__class__.__name__
        self.setObjectName(name)
        self._completed: bool = False  # whether the graphql operation completed.
        self._operation_on_the_fly: bool = False
        self._data: Optional[T] = None
        self.environment = get_gql_env(self.ENV_NAME)
        self._variables: dict = {}
        self._consumer: Optional[QmlOperationConsumerABC] = None

    def consume(self, consumer: QmlOperationConsumerABC) -> None:
        self._consumer = consumer
        self.dataChanged.connect(consumer.handlerDataChanged)

    def loose(self) -> None:
        """Releases retention from all children, real implementation is
        generated."""
        raise NotImplementedError

    @slot
    def fetch(self) -> None:
        if not self._operation_on_the_fly and not self._completed:
            self.set_operation_on_flight(True)
            self.environment.client.execute(self)  # type: ignore

    @slot
    def refetch(self) -> None:
        self.set_completed(False)
        self.fetch()

    @property
    def message(self) -> GqlClientMessage:
        self._message_template.payload.variables = self._variables
        return self._message_template

    @qproperty(QObject, notify=dataChanged)
    def data(self) -> Optional[T]:
        return self._data

    def set_completed(self, v: bool) -> None:
        self._completed = v
        self.set_operation_on_flight(False)
        self.completedChanged.emit()

    @qproperty(bool, notify=completedChanged)
    def completed(self):
        return self._completed

    def set_operation_on_flight(self, v: bool) -> None:
        self._operation_on_the_fly = v
        self.operationOnFlightChanged.emit()

    @qproperty(bool, notify=operationOnFlightChanged)
    def operationOnFlight(self) -> bool:
        return self._operation_on_the_fly

    def on_data(self, message: dict) -> None:  # pragma: no cover
        # real is on derived class.
        raise NotImplementedError

    def on_completed(self) -> None:
        # https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md#complete
        self.set_completed(True)

    def on_error(self, message: list[dict[str, Any]]) -> None:
        # https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md#error
        self.set_completed(True)
        self.error.emit(message)

    @slot
    def dispose(self) -> None:
        """Get rid of ownership on related data and set data to null."""
        self.loose()

    def deleteLater(self) -> None:
        self.dispose()
        super().deleteLater()


class BaseQueryHandler(BaseOperationHandler[T]):
    """Each handler will be exposed to QML and."""

    ...


class BaseMutationHandler(BaseOperationHandler[T]):
    @slot
    def commit(self) -> None:
        # ATM this is just an alias, we might add some functionality here later like optimistic updates.
        self.refetch()


class QmlOperationConsumerABC(QQuickItem, Generic[T]):
    # signals
    operationNameChanged = Signal()
    autofetchChanged = Signal()
    handlerDataChanged = Signal()

    def __init__(self, parent: Optional[QQuickItem] = None):
        super().__init__(parent)
        self._autofetch: bool = False
        self._handler: BaseOperationHandler[T] = self._get_handler()
        self._handler.consume(self)
        self.destroyed.connect(self._handler.dispose)  # type: ignore

    @qproperty(type=BaseOperationHandler, constant=True)
    def handler(self) -> BaseOperationHandler[T]:
        return self._handler

    def handlerData(self):  # property
        # real implementation in template.
        raise NotImplementedError

    @slot
    def set_autofetch(self, v: bool) -> None:
        self._autofetch = v
        self.autofetchChanged.emit()

    @qproperty(type=bool, notify=autofetchChanged, fset=set_autofetch)
    def autofetch(self) -> bool:
        return self._autofetch

    def componentComplete(self) -> None:
        if self._autofetch:
            self._handler.fetch()
        super().componentComplete()

    @classmethod
    def _get_handler(cls) -> BaseOperationHandler[T]:
        # real implementation is generated.
        raise NotImplementedError
