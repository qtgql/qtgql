#include "./gqltransport.hpp"

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
  connect(&m_ws,
          QOverload<QAbstractSocket::SocketError>::of(&QWebSocket::error), this,
          &GqlWsTransportClient::onError);

  auto req = QNetworkRequest(m_url);
  if (headers.has_value()) {
    auto _headers = headers.value();
    for (const auto &header : qAsConst(_headers)) {
      req.setRawHeader(header.first.toUtf8(), header.second.toUtf8());
    }
  }
  init_connection(req);
}

void GqlWsTransportClient::send_message(const GqlClientMessage &message) {
  m_ws.sendBinaryMessage(QJsonDocument(message.serialize()).toJson());
}

void GqlWsTransportClient::init_connection(const QNetworkRequest &request) {
  this->m_ws.open(request, this->m_ws_options);
}

bool GqlWsTransportClient::gql_is_valid() {
  return m_ws.isValid() && m_connection_ack;
}

void GqlWsTransportClient::execute(std::shared_ptr<GqlWsHandlerABC> handler) {
  auto message = handler->message();
  m_handlers.insert(message.id, handler);
  if (m_ws.isValid()) {
    send_message(message);
  } else {
    m_pending_handlers << handler;  // refcount increased (copy constructor)
  }
};
