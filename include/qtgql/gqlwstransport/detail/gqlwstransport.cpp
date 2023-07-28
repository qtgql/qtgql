#include "gqlwstransport.hpp"

namespace qtgql::gqlwstransport {

GqlWsTransport::GqlWsTransport(const GqlWsTransportClientSettings &settings)
    : m_url{settings.url}, QObject::QObject(settings.parent) {
  m_ws = new QWebSocket();
  m_ws->setParent(this);
  m_auto_reconnect = settings.auto_reconnect;
  m_reconnect_timer = new QTimer(this);
  if (settings.auto_reconnect) {
    m_reconnect_timer->setInterval(settings.reconnect_timeout);
    connect(m_reconnect_timer, &QTimer::timeout, this,
            &GqlWsTransport::onReconnectTimeout);
  }
  m_ping_timer = new QTimer(this);
  m_ping_timer->setInterval(settings.ping_interval);
  connect(m_ping_timer, &QTimer::timeout, this, &GqlWsTransport::onPingTimeout);

  m_ping_tester_timer = new QTimer(this);
  m_ping_tester_timer->setInterval(settings.ping_timeout);
  connect(m_ping_tester_timer, &QTimer::timeout, this,
          &GqlWsTransport::onPingTesterTimeout);

  m_ws_options = QWebSocketHandshakeOptions();
  m_ws_options.setSubprotocols(QList<QString>{
      this->SUB_PROTOCOL,
  });
  connect(m_ws, &QWebSocket::textMessageReceived, this,
          &GqlWsTransport::onTextMessageReceived);
  connect(m_ws, &QWebSocket::connected, this, &GqlWsTransport::onConnected);
  connect(m_ws, &QWebSocket::disconnected, this,
          &GqlWsTransport::onDisconnected);

#if QT_VERSION < QT_VERSION_CHECK(6, 5, 0)
  connect(m_ws, QOverload<QAbstractSocket::SocketError>::of(&QWebSocket::error),
          this, &GqlWsTransportClient::onError);
#else

  connect(m_ws, &QWebSocket::errorOccurred, this, &GqlWsTransport::onError);
#endif

  auto req = QNetworkRequest(m_url);
  if (!settings.headers.empty()) {
    for (const auto &header : qAsConst(settings.headers)) {
      req.setRawHeader(header.first.toUtf8(), header.second.toUtf8());
    }
  }
  init_connection(req);
}

void GqlWsTransport::on_gql_next(const GqlWsTrnsMsgWithID &message) {
  if (message.has_payload()) {
    if (m_connected_handlers.contains(message.op_id)) {
      m_connected_handlers.at(message.op_id)
          ->on_next(message.payload.value("data").toObject());
    }
  }
}

void GqlWsTransport::on_gql_error(const GqlWsTrnsMsgWithID &message) {
  qWarning() << "GraphQL Error occurred on ID: " << message.op_id.toString();
  qWarning() << message.errors;
  if (message.has_errors()) {
    if (m_connected_handlers.contains(message.op_id)) {
      m_connected_handlers.at(message.op_id)->on_error(message.errors);
    }
  }
}

void GqlWsTransport::on_gql_complete(const GqlWsTrnsMsgWithID &message) {
  if (m_connected_handlers.contains(message.op_id)) {
    auto handler = m_connected_handlers[message.op_id];
    handler->on_completed();
    m_connected_handlers.erase(message.op_id);
  }
}

void GqlWsTransport::on_gql_ack() {
  send_message(DEF_MESSAGES::PING);
  m_ping_timer->start();
  m_ping_tester_timer->start();
  m_connection_ack = true;
  auto i = m_pending_handlers.begin();
  // If a handler was executed successfully we should remove it from
  // the set.
  while (i != m_pending_handlers.end()) {
    const auto &handler = (*i);
    qDebug() << "re-executing handler with id: " << handler->id;
    execute(handler);
    if (m_connected_handlers.contains(handler->id)) {
      m_pending_handlers.erase(i++);
    } else {
      ++i;
    }
  }
}

void GqlWsTransport::on_gql_pong() { m_ping_tester_timer->stop(); }

void GqlWsTransport::on_gql_ping() { send_message(DEF_MESSAGES::PONG); }

void GqlWsTransport::onReconnectTimeout() {
  if (!m_ws->isValid() || !m_connection_ack) {
    reconnect();
  }
}

void GqlWsTransport::onPingTimeout() {
  send_message(DEF_MESSAGES::PING);
  m_ping_tester_timer->start();
}

void GqlWsTransport::onPingTesterTimeout() {
  qDebug() << "pong timeout reached, endpoint (" << m_url.toDisplayString()
           << ") did not send a pong the configured maximum delay";
  m_ws->close(QWebSocketProtocol::CloseCodeReserved1004);
  m_ping_tester_timer->stop();
}

void GqlWsTransport::send_message(const bases::HashAbleABC &message) {
  m_ws->sendTextMessage(QJsonDocument(message.serialize()).toJson());
}

void GqlWsTransport::onTextMessageReceived(const QString &message) {
  auto raw_data = QJsonDocument::fromJson(message.toUtf8());
  if (raw_data.isObject()) {
    auto data = raw_data.object();
    if (data.contains("id")) {
      // Any that contains ID is directed to a single handler.
      auto message = GqlWsTrnsMsgWithID(data);
      auto message_type = message.type;
      if (message_type == PROTOCOL::NEXT) {
        on_gql_next(message);
      } else if (message_type == PROTOCOL::ERROR) {
        on_gql_error(message);
      } else if (message_type == PROTOCOL::COMPLETE) {
        on_gql_complete(message);
      }
    } else {
      auto message = BaseGqlWsTrnsMsg(data);
      auto message_type = message.type;
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

void GqlWsTransport::onConnected() {
  qDebug() << "Connection established on url " << m_url.toDisplayString();
  send_message(DEF_MESSAGES::CONNECTION_INIT);
  if (m_reconnect_timer->isActive()) {
    m_reconnect_timer->stop();
  }
}

void GqlWsTransport::onDisconnected() {
  m_connection_ack = false;
  qWarning() << "disconnected from " << m_url.toDisplayString()
             << "close code: " << m_ws->closeCode()
             << " reason: " << m_ws->closeReason();
  m_ping_timer->stop();
  m_ping_tester_timer->stop();
  for (const auto &id_handler_pair : m_connected_handlers) {
    m_pending_handlers.insert(id_handler_pair.second);
  };
  m_connected_handlers.clear();
  if (m_auto_reconnect) {
    reconnect();
    m_reconnect_timer->start();
  }
}

void GqlWsTransport::onError(const QAbstractSocket::SocketError &error) {
  qDebug() << "connection error occurred in " << typeid(this).name() << ": "
           << error;
}

void GqlWsTransport::init_connection(const QNetworkRequest &request) {
  this->m_ws->open(request, this->m_ws_options);
}

void GqlWsTransport::close(QWebSocketProtocol::CloseCode closeCode,
                           const QString &reason) {
  m_ws->close(closeCode, reason);
}
// whether the web socket us connected.
bool GqlWsTransport::is_valid() const { return m_ws->isValid(); }

bool GqlWsTransport::gql_is_valid() const {
  return is_valid() && m_connection_ack;
}

void GqlWsTransport::execute(
    const std::shared_ptr<bases::HandlerABC> &handler) {
  if (!m_connected_handlers.contains(handler->id)) {
    // if GQL_ACK and connected
    // send message and delete the pending handler it is now "connected".
    if (gql_is_valid()) {
      m_connected_handlers[handler->id] = handler;
      send_message(GqlWsTrnsMsgWithID(handler->message(), handler->id));
    } else if (!m_pending_handlers.contains(handler)) {
      m_pending_handlers.insert(handler);
    }
  }
}

void GqlWsTransport::reconnect() {
  this->m_ws->open(m_ws->request(), m_ws_options);
}
} // namespace qtgql::gqlwstransport
