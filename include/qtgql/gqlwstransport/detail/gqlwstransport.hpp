#pragma once
#include <QJsonObject>
#include <QUuid>
#include <QWebSocket>
#include <QWebSocketHandshakeOptions>
#include <QtCore>
#include <deque>
#include <memory>
#include <optional>
#include <unordered_set>

#include "qtgql/bases/bases.hpp"

#include "tools.hpp"

namespace qtgql::gqlwstransport {

// The WebSocket sub-protocol for this specification is: graphql-transport-
// ws.
// https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md
namespace PROTOCOL {
inline const QString CONNECTION_INIT = "connection_init";
inline const QString CONNECTION_ACK = "connection_ack";
inline const QString ERROR = "error";
inline const QString COMPLETE = "complete";
inline const QString NEXT = "next";
inline const QString PING = "ping";
inline const QString PONG = "pong";
inline const QString SUBSCRIBE =
    "subscribe"; // for queries | mutations as well.
};               // namespace PROTOCOL

struct BaseGqlWsTrnsMsg : public bases::HashAbleABC {
  QString type;
  QJsonObject payload;

  BaseGqlWsTrnsMsg(const QString &type) {
    assert(!type.isEmpty());
    this->type = type;
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

  [[nodiscard]] QJsonObject serialize() const override {
    QJsonObject data;
    data["type"] = type;
    if (!payload.isEmpty()) {
      data["payload"] = payload;
    }
    return data;
  }
};

struct GqlWsTrnsMsgWithID : public BaseGqlWsTrnsMsg {
  QJsonArray errors;
  QUuid op_id;

  explicit GqlWsTrnsMsgWithID(const QJsonObject &data)
      : BaseGqlWsTrnsMsg(data) { // NOLINT
    this->op_id = QUuid::fromString(data["id"].toString());
    if (this->type == PROTOCOL::ERROR) {
      errors = data.value("payload").toArray();
    }
  }

  explicit GqlWsTrnsMsgWithID(const bases::GraphQLMessage &payload,
                              QUuid id = QUuid::createUuid())
      : BaseGqlWsTrnsMsg(PROTOCOL::SUBSCRIBE, payload.serialize()),
        op_id{id} {};

  bool has_errors() const { return !this->errors.isEmpty(); }

  [[nodiscard]] QJsonObject serialize() const override {
    QJsonObject ret = BaseGqlWsTrnsMsg::serialize();
    ret["id"] = op_id.toString();
    return ret;
  }
};

namespace DEF_MESSAGES {
const auto CONNECTION_INIT = BaseGqlWsTrnsMsg(PROTOCOL::CONNECTION_INIT);
const auto PING = BaseGqlWsTrnsMsg(PROTOCOL::PING);
const auto PONG = BaseGqlWsTrnsMsg(PROTOCOL::PONG);
} // namespace DEF_MESSAGES

struct GqlWsTransportClientSettings {
  const QUrl url;
  QObject *parent = nullptr;
  int ping_interval = 50000;
  int ping_timeout = 5000;
  int reconnect_timeout = 3000;
  bool auto_reconnect = false;
  const QList<std::pair<QString, QString>> headers = {};
};

class GqlWsTransportClient : public QObject, public bases::NetworkLayer {
  Q_OBJECT

private:
  GqlWsTransportClient() = delete;

  void send_message(const bases::HashAbleABC &message);

private Q_SLOTS:

  void onReconnectTimeout();

  void onPingTimeout();

  void onPingTesterTimeout();

protected:
  QUrl m_url;
  bool m_auto_reconnect = true;
  bool m_connection_ack = false;
  QTimer *m_reconnect_timer;
  QTimer *m_ping_timer;
  QTimer *m_ping_tester_timer;
  QWebSocket m_ws;
  QWebSocketHandshakeOptions m_ws_options;

  std::map<QUuid, std::shared_ptr<bases::HandlerABC>> m_handlers;
  // handlers that theirs execution was deferred due to connection issues.
  std::unordered_set<std::shared_ptr<bases::HandlerABC>> m_pending_handlers;

  // general protocol handlers:
  void on_gql_ack();

  void on_gql_pong();

  void on_gql_ping();

  virtual void on_gql_next(const GqlWsTrnsMsgWithID &message);

  virtual void on_gql_error(const GqlWsTrnsMsgWithID &message);

  virtual void on_gql_complete(const GqlWsTrnsMsgWithID &message);

  void init_connection(const QNetworkRequest &request);

protected Q_SLOTS:

  virtual void onTextMessageReceived(const QString &raw_message);

  void onConnected();

  void onDisconnected();

  void onError(const QAbstractSocket::SocketError &error);

public:
  inline static const QString SUB_PROTOCOL = "graphql-transport-ws";

  explicit GqlWsTransportClient(const GqlWsTransportClientSettings &settings);

  void close(QWebSocketProtocol::CloseCode closeCode =
                 QWebSocketProtocol::CloseCodeNormal,
             const QString &reason = QString());

  bool is_valid() const;

  // whether received connection_ack message and ws is valid.
  bool gql_is_valid() const;

  // execute / pend a handler for execution.
  void execute(const std::shared_ptr<bases::HandlerABC> &handler) override;

  // reconnect with previous settings.
  void reconnect();
};

} // namespace qtgql::gqlwstransport
