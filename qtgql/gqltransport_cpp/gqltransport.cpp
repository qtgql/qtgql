#include "./gqltransport.hpp"

GqlWsTransportClient::GqlWsTransportClient(
    QUrl url, QObject *parent, int ping_interval, int ping_timeout,
    int reconnect_timeout, bool auto_reconnect,
    std::optional<std::pair<QString, QString> > headers)
    : QWebSocket::QWebSocket() {
  m_url = url;
  m_handlers = QMap<QString, GqlWsHandlerABC>{};
  m_pendeing_messages = std::deque<GqlClientMessage>{};
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
  connect(this, &QWebSocket::textMessageReceived, this,
          &GqlWsTransportClient::onTextMessageReceived);
  connect(this, &QWebSocket::connected, this,
          &GqlWsTransportClient::onConnected);
  connect(this, &QWebSocket::disconnected, this,
          &GqlWsTransportClient::onDisconnected);
  connect(this, QOverload<QAbstractSocket::SocketError>::of(&QWebSocket::error),
          this, &GqlWsTransportClient::onError);
}
