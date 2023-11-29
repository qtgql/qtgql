#include "gqltransportws.hpp"

namespace qtgql::gqltransportws {

GqlTransportWs::GqlTransportWs(const GqlTransportWsClientSettings &settings)
    : m_settings(settings), QObject::QObject(nullptr) {
  m_ws = new QWebSocket();
  m_ws->setParent(this);
  m_auto_reconnect = m_settings.auto_reconnect;
  m_reconnect_timer = new QTimer(this);
  if (m_settings.auto_reconnect) {
    m_reconnect_timer->setInterval(m_settings.reconnect_timeout);
    connect(m_reconnect_timer, &QTimer::timeout, this,
            &GqlTransportWs::onReconnectTimeout);
  }
  m_ping_timer = new QTimer(this);
  m_ping_timer->setInterval(m_settings.ping_interval);
  connect(m_ping_timer, &QTimer::timeout, this, &GqlTransportWs::onPingTimeout);

  m_ping_tester_timer = new QTimer(this);
  m_ping_tester_timer->setInterval(m_settings.ping_timeout);
  connect(m_ping_tester_timer, &QTimer::timeout, this,
          &GqlTransportWs::onPingTesterTimeout);

  m_ws_options = QWebSocketHandshakeOptions();
  m_ws_options.setSubprotocols(QList<QString>{
      SUB_PROTOCOL,
  });
  connect(m_ws, &QWebSocket::textMessageReceived, this,
          &GqlTransportWs::onTextMessageReceived);
  connect(m_ws, &QWebSocket::connected, this, &GqlTransportWs::onConnected);
  connect(m_ws, &QWebSocket::disconnected, this,
          &GqlTransportWs::onDisconnected);

#if QT_VERSION < QT_VERSION_CHECK(6, 5, 0)
  connect(m_ws, QOverload<QAbstractSocket::SocketError>::of(&QWebSocket::error),
          this, &GqlWsTransportClient::onError);
#else

  connect(m_ws, &QWebSocket::errorOccurred, this, &GqlTransportWs::onError);
#endif
  init_connection();
}

void GqlTransportWs::on_gql_next(const GqlTrnsWsMsgWithID &message) {
  if (message.has_payload()) {
    if (m_connected_handlers.contains(message.op_id)) {
      m_connected_handlers.at(message.op_id)
          ->on_next(message.payload.value("data").toObject());
    }
  }
}

void GqlTransportWs::on_gql_error(const GqlTrnsWsMsgWithID &message) {
  if (message.has_errors()) {
    if (m_connected_handlers.contains(message.op_id)) {
      auto handler = m_connected_handlers.at(message.op_id);
      qWarning() << "GraphQL Error occurred on operation"
                 << handler->message().operationName
                 << " ID: " << message.op_id.toString();
      qWarning() << message.errors;
      handler->on_error(message.errors);
    }
  }
}

void GqlTransportWs::on_gql_complete(const GqlTrnsWsMsgWithID &message) {
  if (m_connected_handlers.contains(message.op_id)) {
    auto handler = m_connected_handlers[message.op_id];
    handler->on_completed();
    m_connected_handlers.erase(message.op_id);
  }
}

void GqlTransportWs::on_gql_ack() {
  send_message(DEF_MESSAGES::PING);
  m_ping_timer->start();
  m_ping_tester_timer->start();
  m_connection_ack = true;
  auto i = m_pending_handlers.begin();
  // If a handler was executed successfully we should remove it from
  // the set.
  while (i != m_pending_handlers.end()) {
    const auto &uuid_handler = (*i);
    qDebug() << "re-executing handler with id: " << uuid_handler.first;
    execute_impl(uuid_handler.first, uuid_handler.second);
    if (m_connected_handlers.contains(uuid_handler.first)) {
      m_pending_handlers.erase(i++);
    } else {
      ++i;
    }
  }
}

void GqlTransportWs::on_gql_pong() { m_ping_tester_timer->stop(); }

void GqlTransportWs::on_gql_ping() { send_message(DEF_MESSAGES::PONG); }

void GqlTransportWs::onReconnectTimeout() {
  if (!m_ws->isValid() || !m_connection_ack) {
    reconnect();
  }
}

void GqlTransportWs::onPingTimeout() {
  send_message(DEF_MESSAGES::PING);
  m_ping_tester_timer->start();
}

void GqlTransportWs::onPingTesterTimeout() {
  qDebug() << "pong timeout reached, endpoint ("
           << m_settings.url.toDisplayString()
           << ") did not send a pong the configured maximum delay";
  m_ws->close(QWebSocketProtocol::CloseCodeReserved1004);
  m_ping_tester_timer->stop();
}

void GqlTransportWs::send_message(const bases::HashAbleABC &message) {

  m_ws->sendTextMessage(QJsonDocument(message.serialize()).toJson());
}

void GqlTransportWs::send_message(const bases::HashAbleABC &message,
                                  QUuid uuid) {
  QJsonObject msg = message.serialize();
  msg.insert("id", uuid.toString());
  m_ws->sendTextMessage(QJsonDocument(msg).toJson());
}

void GqlTransportWs::onTextMessageReceived(const QString &message) {
  auto raw_data = QJsonDocument::fromJson(message.toUtf8());
  if (raw_data.isObject()) {
    auto data = raw_data.object();
    if (data.contains("id")) {
      auto uuid = data.value("id");
      // Any that contains ID is directed to a single handler.
      auto op_message = GqlTrnsWsMsgWithID(data);
      auto message_type = op_message.type;
      if (message_type == PROTOCOL::NEXT) {
        on_gql_next(op_message);
      } else if (message_type == PROTOCOL::ERROR) {
        on_gql_error(op_message);
      } else if (message_type == PROTOCOL::COMPLETE) {
        on_gql_complete(op_message);
      }
    } else {
      auto conn_message = BaseGqlTrnsWsMsg(data);
      auto message_type = conn_message.type;
      if (message_type == PROTOCOL::CONNECTION_ACK) {
        on_gql_ack();
      } else if (message_type == PROTOCOL::PONG) {
        on_gql_pong();
      } else if (message_type == PROTOCOL::PING) {
        on_gql_ping();
      }
    }
  }
}

void GqlTransportWs::onConnected() {
  qDebug() << "Connection established on url "
           << m_settings.url.toDisplayString();
  send_message(DEF_MESSAGES::CONNECTION_INIT);
  if (m_reconnect_timer->isActive()) {
    m_reconnect_timer->stop();
  }
}

void GqlTransportWs::onDisconnected() {
  m_connection_ack = false;
  qWarning() << "disconnected from " << m_settings.url.toDisplayString()
             << "close code: " << m_ws->closeCode()
             << " reason: " << m_ws->closeReason();
  m_ping_timer->stop();
  m_ping_tester_timer->stop();
  for (const auto &id_handler_pair : m_connected_handlers) {
    m_pending_handlers.insert(id_handler_pair);
  };
  m_connected_handlers.clear();
  if (m_auto_reconnect) {
    reconnect();
    m_reconnect_timer->start();
  }
}

void GqlTransportWs::onError(const QAbstractSocket::SocketError &error) {
  qWarning() << "connection error occurred in " << typeid(this).name() << ": "
             << error;
}

void GqlTransportWs::init_connection() {
  auto req = QNetworkRequest(m_settings.url);
  if (!m_settings.headers.empty()) {
    for (const auto &[key, value] : m_settings.headers) {
      req.setRawHeader(key.toUtf8(), value.toUtf8());
    }
  }
  this->m_ws->open(req, m_ws_options);
}

void GqlTransportWs::close(QWebSocketProtocol::CloseCode closeCode,
                           const QString &reason) {
  m_ws->close(closeCode, reason);
}
// whether the web socket us connected.
bool GqlTransportWs::is_valid() const { return m_ws->isValid(); }

bool GqlTransportWs::gql_is_valid() const {
  return is_valid() && m_connection_ack;
}

void GqlTransportWs::execute(const std::shared_ptr<bases::HandlerABC> &handler,
                             QUuid op_id) {
  execute_impl(op_id, handler);
}
void GqlTransportWs::execute_impl(
    const QUuid &op_id, const std::shared_ptr<bases::HandlerABC> &handler) {
  // check if there is a same subscription with different uuid
  auto i = m_connected_handlers.begin();
  while (i != m_connected_handlers.end()) {
    const auto &uuid_handler = (*i);
    if (uuid_handler.second->message().query == handler->message().query) {
      // send complete message to server
      send_message(DEF_MESSAGES::COMPLETE, op_id);
      uuid_handler.first.fromString(op_id.toString());
      break;
    }
    i++;
  }
  // if GQL_ACK and connected
  // send a message and delete the pending handler, it is now "connected".
  if (!m_connected_handlers.contains(op_id)) {
    if (gql_is_valid()) {
      m_connected_handlers[op_id] = handler;
      send_message(GqlTrnsWsMsgWithID(handler->message(), op_id));
    } else if (!m_pending_handlers.contains(op_id)) {
      m_pending_handlers[op_id] = handler;
    }
  }
}
void GqlTransportWs::set_headers(const std::map<QString, QString> &headers) {
  m_settings.headers = headers;
}

void GqlTransportWs::reconnect() {
  //  uncompleted handlers are delayed in `on_disconnected`
  close(QWebSocketProtocol::CloseCode::CloseCodeNormal);
  init_connection();
}

} // namespace qtgql::gqltransportws
