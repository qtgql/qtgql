import json
import logging
import typing
import uuid
from abc import abstractmethod
from collections import deque
from typing import Any, Optional

from attrs import define, field
from PySide6 import QtCore, QtNetwork, QtWebSockets

from qtgql.gqltransport.core import EncodeAble, GqlEncoder, QueryPayload, T
from qtgql.tools import slot
from qtgql.utils.typingref import UNSET

logger = logging.getLogger(__name__)

__all__ = ["HandlerProto", "GqlWsTransportClient"]


class PROTOCOL:
    """The WebSocket sub-protocol for this specification is: graphql-transport-
    ws.

    https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md
    """

    CONNECTION_INIT = "connection_init"
    CONNECTION_ACK = "connection_ack"
    NEXT = "next"
    ERROR = "error"
    COMPLETE = "complete"
    PING = "ping"
    PONG = "pong"
    SUBSCRIBE = "subscribe"


@define(kw_only=True)
class BaseGqlWsTransportMessage(EncodeAble):
    type: str
    payload: Optional[Any] = UNSET


@define(kw_only=True)
class GqlClientMessage(typing.Generic[T], BaseGqlWsTransportMessage):
    id: str = field(factory=lambda: uuid.uuid4().hex)
    type: str = PROTOCOL.SUBSCRIBE
    payload: QueryPayload[T] = UNSET

    @classmethod
    def from_query(cls, query: str) -> "GqlClientMessage":
        return cls(payload=QueryPayload(query=query))


@define(kw_only=True)
class SubscribeResponseMessage(BaseGqlWsTransportMessage):
    id: str


class HandlerProto(typing.Protocol):  # pragma: no cover
    message: GqlClientMessage

    @abstractmethod
    def on_data(self, message: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def on_error(self, message: list[dict[str, Any]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def on_completed(self) -> None:
        raise NotImplementedError


class MESSAGES:
    CONNECTION_INIT = BaseGqlWsTransportMessage(type=PROTOCOL.CONNECTION_INIT)
    PING = BaseGqlWsTransportMessage(type=PROTOCOL.PING)
    PONG = BaseGqlWsTransportMessage(type=PROTOCOL.PONG)


class GqlWsTransportClient(QtWebSockets.QWebSocket):
    SUB_PROTOCOL = "graphql-transport-ws"
    textMessageReceived: QtCore.Signal
    connected: QtCore.Signal
    disconnected: QtCore.Signal
    error: QtCore.Signal  # type: ignore

    def __init__(
        self,
        *,
        url: str,
        parent=None,
        ping_interval: int = 50000,
        ping_timeout: int = 5000,
        auto_reconnect: bool = False,
        reconnect_timeout: int = 5000,
        headers: Optional[dict[bytes, bytes]] = None,
    ):
        super().__init__(parent=parent)
        self._ping_is_valid = True
        self._connection_ack = False
        self.reconnect_timer = QtCore.QTimer(self)
        if auto_reconnect:
            self.reconnect_timer.setInterval(reconnect_timeout)
            self.reconnect_timer.timeout.connect(self.on_reconnect_timeout)  # type: ignore

        self.url: QtCore.QUrl = QtCore.QUrl(url)
        self.handlers: dict[str, HandlerProto] = {}
        self.pending_messages: deque[GqlClientMessage] = deque()
        self.ping_timer = QtCore.QTimer(self)
        self.ping_timer.setInterval(ping_interval)
        self.ping_timer.timeout.connect(self._on_ping_timeout)  # type: ignore
        self.ping_tester_timer = QtCore.QTimer(self)
        self.ping_tester_timer.setInterval(ping_timeout)
        self.ping_tester_timer.timeout.connect(self._on_ping_tester_timeout)  # type: ignore
        self.ws_options = QtWebSockets.QWebSocketHandshakeOptions()
        self.ws_options.setSubprotocols(
            [
                self.SUB_PROTOCOL,
            ]
        )
        self.textMessageReceived.connect(self.on_text_message)
        self.connected.connect(self._on_connected)
        self.disconnected.connect(self.on_disconnected)
        self.error.connect(self.on_error)
        req = QtNetwork.QNetworkRequest(self.url)
        req.setUrl(self.url)
        if headers:
            for name, value in headers.items():
                req.setRawHeader(name, value)
        self._init_connection(req)

    def _init_connection(self, request: QtNetwork.QNetworkRequest) -> None:
        """Instantiate the connection with server."""
        self.open(request, self.ws_options)

    @staticmethod
    def dumps(data: Any) -> str:
        return json.dumps(data, cls=GqlEncoder)

    def gql_is_valid(self) -> bool:
        """return True if the CONNECTION_ACK has been received and ping is
        valid."""
        return self.isValid() and self._connection_ack

    def execute(self, handler: HandlerProto) -> None:
        client_id = handler.message.id
        self.handlers[client_id] = handler
        if self.isValid():
            self.run_subscription(handler.message)
        else:
            self.pending_messages.append(handler.message)

    def run_subscription(self, message: GqlClientMessage) -> None:
        self.sendTextMessage(self.dumps(message))

    def _on_connected(self):
        logger.info(
            "{classname}: connection established with server {url}!",
            extra={
                "classname": self.__class__.__name__,
                "url": self.url.toString(),
            },
        )
        self.sendTextMessage(self.dumps(MESSAGES.CONNECTION_INIT))
        if self.reconnect_timer.isActive():
            self.reconnect_timer.stop()

    def on_disconnected(self):
        logger.warning(
            "disconnected from {url} because: {}; " "close code: {closeCodeName}: {closeCodeV}",
            extra={
                "url": self.url.toString(),
                "closeReason": self.closeReason(),
                "closeCodeV": self.closeCode().value,
                "closeCodeName": self.closeCode().name,
            },
        )
        self.ping_timer.stop()
        self.ping_tester_timer.stop()
        self.reconnect_timer.start()

    def on_error(self, error: QtNetwork.QAbstractSocket.SocketError):  # pragma: no cover
        logger.warning(
            "error occurred in {className}: {error}",
            extra={"className": self.__class__.__name__, "error": error},
        )
        if not self.isValid():
            self.reconnect_timer.start()

    @slot
    def on_reconnect_timeout(self) -> None:
        if not self.isValid():
            self._init_connection(self.request())

    def on_text_message(self, raw: str) -> None:
        data = json.loads(raw)
        if data.get("id", None):
            message = SubscribeResponseMessage(**data)
            m_type = message.type
            if m_type == PROTOCOL.NEXT:
                self._on_gql_next(message)
            elif m_type == PROTOCOL.ERROR:
                self._on_gql_error(message)
            elif m_type == PROTOCOL.COMPLETE:
                self._on_gql_complete(message)
        else:
            # these are id agnostic handlers.
            message = BaseGqlWsTransportMessage(**data)  # type: ignore
            m_type = message.type
            if m_type == PROTOCOL.CONNECTION_ACK:
                self._on_gql_ack()
            elif m_type == PROTOCOL.PONG:
                self._on_gql_pong()
            elif m_type == PROTOCOL.PING:
                self._on_gql_ping()

    def _on_ping_timeout(self):
        self.sendTextMessage(self.dumps(MESSAGES.PING))
        self.ping_tester_timer.start()

    def _on_ping_tester_timeout(self):
        logger.warning("pong timeout reached on {url}", extra={"url": self.requestUrl().url()})
        self.close(
            QtWebSockets.QWebSocketProtocol.CloseCode.CloseCodeReserved1004, "Pong timeout reached"
        )
        self.ping_tester_timer.stop()

    def _on_gql_ack(self) -> None:
        self.sendTextMessage(self.dumps(MESSAGES.PING))
        self.ping_timer.start()
        self.ping_tester_timer.start()
        self._connection_ack = True
        while self.pending_messages:
            self.run_subscription(self.pending_messages.popleft())

    def _on_gql_pong(self) -> None:
        self.ping_tester_timer.stop()

    def _on_gql_ping(self) -> None:
        self.sendTextMessage(self.dumps(MESSAGES.PONG))

    def _on_gql_error(self, message: SubscribeResponseMessage):
        logger.warning("GQL error occurred: %s", message)
        if message.payload:
            self.handlers[message.id].on_error(message.payload)

    def _on_gql_complete(self, message: SubscribeResponseMessage) -> None:
        handler = self.handlers.pop(message.id)
        handler.on_completed()

    def _on_gql_next(self, message: SubscribeResponseMessage) -> None:
        if message.payload:
            self.handlers[message.id].on_data(message.payload["data"])
