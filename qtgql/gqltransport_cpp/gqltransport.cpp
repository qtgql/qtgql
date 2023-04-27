#include "./gqltransport.hpp"

#include <QtGlobal>

GqlWsTransportClient::GqlWsTransportClient(
    QUrl url, QObject *parent, int ping_interval, int ping_timeout,
    int reconnect_timeout, bool auto_reconnect,
    std::optional<QList<std::pair<QString, QString>>> headers)
    : QObject::QObject(parent), m_url{url} {
  m_reconnect_timer = new QTimer(this);
  if (auto_reconnect) {
    m_reconnect_timer->setInterval(reconnect_timeout);
    connect(m_reconnect_timer, &QTimer::timeout, this,
            &GqlWsTransportClient::onReconnectTimeout);
  }
  m_ping_timer = new QTimer(this);
  m_ping_timer->setInterval(ping_interval);
  connect(m_ping_timer, &QTimer::timeout, this,
          &GqlWsTransportClient::onPingTimeout);

  m_ping_tester_timer = new QTimer(this);
  m_ping_tester_timer->setInterval(ping_timeout);
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
  if (headers.has_value()) {
    auto _headers = headers.value();
    for (const auto &header : qAsConst(_headers)) {
      req.setRawHeader(header.first.toUtf8(), header.second.toUtf8());
    }
  }
  init_connection(req);
}

void GqlWsTransportClient::on_gql_next(const GqlWsTrnsMsgWithID &message) {
  if (message.has_payload()) {
    if (m_handlers.contains(message.id)) {
      auto handler = m_handlers.value(message.id);
      handler->onData(message.payload.toVariantMap());
    }
  }
}

void GqlWsTransportClient::on_gql_error(const GqlWsTrnsMsgWithID &message) {
  qWarning() << "GraphQL Error occurred on ID: " << message.id.toString();
  if (message.has_payload()) {
    if (m_handlers.contains(message.id)) {
      m_handlers.value(message.id)->onError(message.payload.toVariantMap());
    }
  }
}

void GqlWsTransportClient::on_gql_complete(const GqlWsTrnsMsgWithID &message) {
  if (m_handlers.contains(message.id)) {
    auto handler = m_handlers.value(message.id);
    handler->onCompleted();
    m_handlers.remove(message.id);
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
  if (!m_ws.isValid()) {
    init_connection(m_ws.request());
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

void GqlWsTransportClient::send_message(const BaseGqlWsTrnsMsg &message) {
  m_ws.sendBinaryMessage(QJsonDocument(message.serialize()).toJson());
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
  qDebug() << "disconnected from " << m_url.toDisplayString()
           << "close code: " << m_ws.closeCode() << " : " << m_ws.closeReason();
  m_ping_timer->stop();
  m_ping_tester_timer->stop();
  m_reconnect_timer->start();
}

void GqlWsTransportClient::onError(const QAbstractSocket::SocketError &error) {
  qDebug() << "connection error occurred in " << typeid(this).name() << ": "
           << error;
}

void GqlWsTransportClient::init_connection(const QNetworkRequest &request) {
  this->m_ws.open(request, this->m_ws_options);
}

bool GqlWsTransportClient::is_valid() { return m_ws.isValid(); }

bool GqlWsTransportClient::gql_is_valid() {
  return is_valid() && m_connection_ack;
}

void GqlWsTransportClient::execute(std::shared_ptr<GqlWsHandlerABC> handler) {
  auto message = handler->message();
  m_handlers.insert(message.id, handler);
  if (m_ws.isValid()) {
    send_message(message);
  } else if (!m_pending_handlers.contains(handler)) {
    m_pending_handlers << handler;  // refcount increased (copy constructor)
  }
}

std::optional<QString> get_operation_name(const QString &query) {
  static QRegularExpression re(
      "(subscription|mutation|query)( [a-zA-Z]+)( |{)");
  auto match = re.match(query);
  if (match.hasMatch()) {
    return match.captured(2);
  }
  return {};
}
