#pragma once
#include <QJsonObject>
#include <QRegularExpression>
#include <QUuid>
#include <QWebSocket>
#include <QWebSocketHandshakeOptions>
#include <QtCore>
#include <deque>
#include <memory>
#include <optional>

// The WebSocket sub-protocol for this specification is: graphql-transport-
// ws.
// https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md
namespace PROTOCOL {
const QString CONNECTION_INIT = "connection_init";
const QString CONNECTION_ACK = "connection_ack";
const QString ERROR = "error";
const QString COMPLETE = "complete";
const QString NEXT = "next";
const QString PING = "pint";
const QString PONG = "pong";
const QString SUBSCRIBE = "subscribe";
};  // namespace PROTOCOL

std::optional<QString> get_operation_name(const QString &query);
;

struct HashAbleABC {
  virtual QJsonObject serialize() const = 0;
};

struct BaseGqlWsTrnsMsg : public HashAbleABC {
  QString type;
  QJsonObject payload = {};
  BaseGqlWsTrnsMsg(const QString &type) {
    this->type = type;
    this->payload = QJsonObject{};
  }

  BaseGqlWsTrnsMsg(const QString &type, const QJsonObject &payload) {
    this->type = type;
    this->payload = payload;
  }

  BaseGqlWsTrnsMsg(const QJsonObject &data) {
    if (data.contains("payload") && data["payload"].isObject()) {
      this->payload = data["payload"].toObject();
    }
    if (data.contains("type") && data["type"].isString()) {
      this->type = data["type"].toString();
    }
  }

  bool has_payload() const { return !payload.isEmpty(); };

  QJsonObject serialize() const {
    QJsonObject data;
    data["type"] = type;
    if (!payload.isEmpty()) {
      data["payload"] = payload;
    }
    return data;
  }
};

struct GqlWsTrnsMsgWithID : public BaseGqlWsTrnsMsg {
  QUuid id = QUuid::createUuid();
  using BaseGqlWsTrnsMsg::BaseGqlWsTrnsMsg;
  GqlWsTrnsMsgWithID(const QJsonObject &data)
      : BaseGqlWsTrnsMsg(data) {  // NOLINT
    this->id = QUuid::fromString(data["id"].toString());
  }
  QJsonObject serialize() const {
    QJsonObject ret = BaseGqlWsTrnsMsg::serialize();
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
const auto CONNECTION_INIT = BaseGqlWsTrnsMsg(PROTOCOL::CONNECTION_INIT);
const auto PING = BaseGqlWsTrnsMsg(PROTOCOL::PING);
const auto PONG = BaseGqlWsTrnsMsg(PROTOCOL::PONG);
}  // namespace DEF_MESSAGES

// Replaces HandlerProto, To be extended by all consumers.
class GqlWsHandlerABC {
 public:
  virtual void onData(QVariantMap message) = 0;
  virtual void onError(QVariantMap message) = 0;
  virtual void onCompleted() = 0;
  virtual const GqlWsTrnsMsgWithID message() = 0;
};

class GqlWsTransportClient : public QObject {
  Q_OBJECT
 private:
  GqlWsTransportClient();  // make the default constructor private.
  QUrl m_url;
  bool m_autoconnect = true;
  bool m_ping_is_valid = true;
  bool m_connection_ack = false;
  QWebSocket m_ws;
  QWebSocketHandshakeOptions m_ws_options;

  QTimer *m_reconnect_timer;
  QTimer *m_ping_timer;
  QTimer *m_ping_tester_timer;

  QMap<QUuid, std::shared_ptr<GqlWsHandlerABC>> m_handlers;
  // handlers that theier execution was deferred due to connection issues.
  QSet<std::shared_ptr<GqlWsHandlerABC>> m_pending_handlers;

  // general protocol handlers:
  void on_gql_ack();
  void on_gql_pong();
  void on_gql_ping();

 private Q_SLOTS:
  void onReconnectTimeout();
  void onPingTimeout();
  void onPingTesterTimeout();
  void send_message(const BaseGqlWsTrnsMsg &message);

 public Q_SLOTS:
  void onTextMessageReceived(const QString &message);
  void onConnected();
  void onDisconnected();
  void onError(const QAbstractSocket::SocketError &error);

 public:
  inline static const QString SUB_PROTOCOL = "graphql-transport-ws";
  GqlWsTransportClient(
      QUrl url, QObject *parent = nullptr, int ping_interval = 50000,
      int ping_timeout = 5000, int reconnect_timeout = 3000,
      bool auto_reconnect = false,
      std::optional<QList<std::pair<QString, QString>>> headers = {});

  void on_gql_next(const GqlWsTrnsMsgWithID &message);
  void on_gql_error(const GqlWsTrnsMsgWithID &message);
  void on_gql_complete(const GqlWsTrnsMsgWithID &message);

  void init_connection(const QNetworkRequest &request);
  bool is_valid();
  bool gql_is_valid();
  void execute(std::shared_ptr<GqlWsHandlerABC> handler);
};
