#pragma once
#include <QJsonObject>
#include <QRegularExpression>
#include <QUuid>
#include <QWebSocket>
#include <QWebSocketHandshakeOptions>
#include <QtCore>
#include <deque>
#include <optional>

// The WebSocket sub-protocol for this specification is: graphql-transport-
// ws.
// https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md
namespace PROTOCOL {
const QString CONNECTION_INIT = "connection_init";
const QString CONNECTION_ACK = "connection_ack";
const QString ERROR = "error";
const QString COMPLETE = "complete";
const QString PING = "pint";
const QString PONG = "pong";
const QString SUBSCRIBE = "subscribe";
};  // namespace PROTOCOL

std::optional<QString> get_operation_name(const QString &query) {
  QRegularExpression re(R"(subscription|mutation|query)(.*?({|\())");
  auto match = re.match(query);
  if (match.hasMatch()) {
    return match.captured(2);
  };
  return {};
};

struct HashAbleABC {
  virtual QJsonObject serialize() const = 0;
};

struct BaseGqlWsTransportMessage : public HashAbleABC {
  QString type;
  QJsonObject payload = {};
  BaseGqlWsTransportMessage(const QString &type) {
    this->type = type;
    this->payload = QJsonObject{};
  }

  BaseGqlWsTransportMessage(const QString &type, const QJsonObject &payload) {
    this->type = type;
    this->payload = payload;
  }

  BaseGqlWsTransportMessage(const QJsonObject &data) {
    if (data.contains("payload") && data["payload"].isObject()) {
      this->payload = data["payload"].toObject();
    }
    if (data.contains("type") && data["type"].isString()) {
      this->type = data["type"].toString();
    }
  }

  QJsonObject serialize() const {
    QJsonObject data;
    data["type"] = type;
    if (!payload.isEmpty()) {
      data["payload"] = payload;
    }
    return data;
  }
};

struct GqlClientMessage : public BaseGqlWsTransportMessage {
  QUuid id = QUuid::createUuid();
  using BaseGqlWsTransportMessage::BaseGqlWsTransportMessage;
  GqlClientMessage(const QJsonObject &data)
      : BaseGqlWsTransportMessage(data) {  // NOLINT
    this->id = QUuid::fromString(data["id"].toString());
  }
  QJsonObject serialize() const {
    QJsonObject ret = BaseGqlWsTransportMessage::serialize();
    ret["id"] = id.toString();
    return ret;
  }
};

struct OperationPayload : public HashAbleABC {
  QString query;
  QString operationName;
  std::optional<QVariant> variables = {};
  OperationPayload(QString query, const QVariant &variables) {
    query = query;
    auto op_name = get_operation_name(query);
    assert(op_name.has_value());
    operationName = op_name.value();
  };
};

struct GqlResult {
  const std::optional<QJsonObject> *data;
  const std::optional<QJsonObject> *errors;
};

namespace DEF_MESSAGES {
const auto CONNECTION_INIT =
    BaseGqlWsTransportMessage(PROTOCOL::CONNECTION_INIT);
const auto PING = BaseGqlWsTransportMessage(PROTOCOL::PING);
const auto PONG = BaseGqlWsTransportMessage(PROTOCOL::PONG);
}  // namespace DEF_MESSAGES

// Replaces HandlerProto, To be extended by all consumers.
class GqlWsHandlerABC {
  void onData(QJsonObject message);
  void onError(QJsonObject message);
  void onCompleted();
};

class GqlWsTransportClient : public QObject {
  Q_OBJECT
 private:
  GqlWsTransportClient();  // make the default constructor private.
  QUrl m_url;
  int m_ping_interval;
  int m_ping_timeout;
  int m_reconnect_timeout;
  bool m_autoconnect = true;
  bool m_ping_is_valid = true;
  bool m_connection_ack = false;
  QWebSocket m_ws;
  QWebSocketHandshakeOptions m_ws_options;

  QTimer *m_reconnect_timer;
  QTimer *m_ping_timer;
  QTimer *m_ping_tester_timer;

  QMap<QString, GqlWsHandlerABC> m_handlers;
  std::deque<GqlClientMessage> m_pendeing_messages;
 private Q_SLOTS:
  void onReconnectTimeout();
  void onPingTimeout();
  void onPingTesterTimeout();
 public Q_SLOTS:
  void onTextMessageReceived(QString message);
  void onConnected();
  void onDisconnected();
  void onError(QAbstractSocket::SocketError error);

 public:
  inline static const QString SUB_PROTOCOL = "graphql-transport-ws";

  GqlWsTransportClient(
      QUrl url, QObject *parent = nullptr, int ping_interval = 50000,
      int ping_timeout = 5000, int reconnect_timeout = 3000,
      bool auto_reconnect = false,
      std::optional<QList<std::pair<QString, QString>>> headers = {});
};
void init_connection(const QNetworkRequest &request);
