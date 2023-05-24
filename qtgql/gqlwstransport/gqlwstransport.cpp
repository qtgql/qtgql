#include "gqlwstransport.hpp"

#include <QtGlobal>
using namespace qtgql;
using namespace gqlwstransport;

GqlWsTransportClient::GqlWsTransportClient(
    const GqlWsTransportClientSettings &settings)
    : m_url{settings.url}, QObject::QObject(settings.parent) {
  m_auto_reconnect = settings.auto_reconnect;
  m_reconnect_timer = new QTimer(this);
  if (settings.auto_reconnect) {
    m_reconnect_timer->setInterval(settings.reconnect_timeout);
    connect(m_reconnect_timer, &QTimer::timeout, this,
            &GqlWsTransportClient::onReconnectTimeout);
  }
  m_ping_timer = new QTimer(this);
  m_ping_timer->setInterval(settings.ping_interval);
  connect(m_ping_timer, &QTimer::timeout, this,
          &GqlWsTransportClient::onPingTimeout);

  m_ping_tester_timer = new QTimer(this);
  m_ping_tester_timer->setInterval(settings.ping_timeout);
  connect(m_ping_tester_timer, &QTimer::timeout, this,
          &GqlWsTransportClient::onPingTesterTimeout);

  m_ws_options = QWebSocketHandshakeOptions();
  m_ws_options.setSubprotocols(QList<QString>{
      this->SUB_PROTOCOL,
  });
  connect(&m_ws, &QWebSocket::textMessageReceived, this,
          &GqlWsTransportClient::onTextMessageReceived);
  connect(&m_ws, &QWebSocket::connected, this,
          &GqlWsTransportClient::onConnected);
  connect(&m_ws, &QWebSocket::disconnected, this,
          &GqlWsTransportClient::onDisconnected);

#if QT_VERSION < QT_VERSION_CHECK(6, 5, 0)
  connect(&m_ws,
          QOverload<QAbstractSocket::SocketError>::of(&QWebSocket::error), this,
          &GqlWsTransportClient::onError);
#else

  connect(&m_ws, &QWebSocket::errorOccurred, this,
          &GqlWsTransportClient::onError);
#endif

  auto req = QNetworkRequest(m_url);
  if (!settings.headers.empty()) {
    for (const auto &header : qAsConst(settings.headers)) {
      req.setRawHeader(header.first.toUtf8(), header.second.toUtf8());
    }
  }
  init_connection(req);
}

void GqlWsTransportClient::on_gql_next(const GqlWsTrnsMsgWithID &message) {
  if (message.has_payload()) {
    if (m_handlers.contains(message.op_id)) {
      auto handler = m_handlers.value(message.op_id);
      handler->on_next(message.payload);
    }
  }
}

void GqlWsTransportClient::on_gql_error(const GqlWsTrnsMsgWithID &message) {
  qWarning() << "GraphQL Error occurred on ID: " << message.op_id.toString();
  if (message.has_errors()) {
    if (m_handlers.contains(message.op_id)) {
      m_handlers.value(message.op_id)->on_error(message.errors);
    }
  }
}

void GqlWsTransportClient::on_gql_complete(const GqlWsTrnsMsgWithID &message) {
  if (m_handlers.contains(message.op_id)) {
    auto handler = m_handlers.value(message.op_id);
    handler->on_completed();
    m_handlers.remove(message.op_id);
  }
}

void GqlWsTransportClient::on_gql_ack() {
  send_message(DEF_MESSAGES::PING);
  m_ping_timer->start();
  m_ping_tester_timer->start();
  m_connection_ack = true;
  for (const auto &pending_handler : qAsConst(m_pending_handlers)) {
    execute(pending_handler);
  }
}

void GqlWsTransportClient::on_gql_pong() { m_ping_tester_timer->stop(); }

void GqlWsTransportClient::on_gql_ping() { send_message(DEF_MESSAGES::PONG); }

void GqlWsTransportClient::onReconnectTimeout() {
  if (!m_ws.isValid() || !m_connection_ack) {
    reconnect();
  }
}

void GqlWsTransportClient::onPingTimeout() {
  send_message(DEF_MESSAGES::PING);
  m_ping_tester_timer->start();
}

void GqlWsTransportClient::onPingTesterTimeout() {
  qDebug() << "pong timeout reached, endpoint (" << m_url.toDisplayString()
           << ") did not send a pong the configured maximum delay";
  m_ws.close(QWebSocketProtocol::CloseCodeReserved1004);
  m_ping_tester_timer->stop();
}

void GqlWsTransportClient::send_message(const bases::HashAbleABC &message) {
  m_ws.sendTextMessage(QJsonDocument(message.serialize()).toJson());
}

void GqlWsTransportClient::onTextMessageReceived(const QString &message) {
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

void GqlWsTransportClient::onConnected() {
  qDebug() << "Connection established on url " << m_url.toDisplayString();
  send_message(DEF_MESSAGES::CONNECTION_INIT);
  if (m_reconnect_timer->isActive()) {
    m_reconnect_timer->stop();
  }
}

void GqlWsTransportClient::onDisconnected() {
  m_connection_ack = false;
  qDebug() << "disconnected from " << m_url.toDisplayString()
           << "close code: " << m_ws.closeCode() << " : " << m_ws.closeReason();
  m_ping_timer->stop();
  m_ping_tester_timer->stop();
  if (m_auto_reconnect) {
    reconnect();
    m_reconnect_timer->start();
  }
}

void GqlWsTransportClient::onError(const QAbstractSocket::SocketError &error) {
  qDebug() << "connection error occurred in " << typeid(this).name() << ": "
           << error;
}

void GqlWsTransportClient::init_connection(const QNetworkRequest &request) {
  this->m_ws.open(request, this->m_ws_options);
}

void GqlWsTransportClient::close(QWebSocketProtocol::CloseCode closeCode,
                                 const QString &reason) {
  m_ws.close(closeCode, reason);
}

bool GqlWsTransportClient::is_valid() const { return m_ws.isValid(); }

bool GqlWsTransportClient::gql_is_valid() const {
  return is_valid() && m_connection_ack;
}

void GqlWsTransportClient::execute(
    const std::shared_ptr<bases::HandlerABC> &handler) {
  m_handlers.insert(handler->operation_id(), handler);
  if (m_ws.isValid()) {
    send_message(handler->message());
    if (m_pending_handlers.contains(handler)) {
      m_pending_handlers.remove(handler);
    }
  } else if (!m_pending_handlers.contains(handler)) {
    m_pending_handlers << handler;  // refcount increased (copy constructor)
  }
}

void GqlWsTransportClient::reconnect() {
  this->m_ws.open(m_ws.request(), m_ws_options);
}
