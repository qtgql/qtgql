#pragma once
#include "qtgql/bases/bases.hpp"
#include "qtgql/qtgql_export.hpp"

#include <QJsonObject>
#include <QUuid>
#include <QWebSocket>
#include <QWebSocketHandshakeOptions>
#include <QtCore>
#include <deque>
#include <memory>
#include <optional>
#include <unordered_set>

namespace qtgql::gqltransportws {

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

struct BaseGqlTrnsWsMsg : public bases::HashAbleABC {
  QString type;
  QJsonObject payload;

  explicit BaseGqlTrnsWsMsg(const QString &type) {
    assert(!type.isEmpty());
    this->type = type;
  }

  BaseGqlTrnsWsMsg(const QString &type, const QJsonObject &payload) {
    this->type = type;
    this->payload = payload;
  }

  explicit BaseGqlTrnsWsMsg(const QJsonObject &data) {
    if (data.contains("payload") && data["payload"].isObject()) {
      this->payload = data["payload"].toObject();
    }
    if (data.contains("type") && data["type"].isString()) {
      this->type = data["type"].toString();
    }
  }

  [[nodiscard]] bool has_payload() const { return !payload.isEmpty(); };

  [[nodiscard]] QJsonObject serialize() const override {
    QJsonObject data;
    data["type"] = type;
    if (!payload.isEmpty()) {
      data["payload"] = payload;
    }
    return data;
  }
};

struct GqlTrnsWsMsgWithID : public BaseGqlTrnsWsMsg {
  QJsonArray errors;
  QUuid op_id;

  explicit GqlTrnsWsMsgWithID(const QJsonObject &data)
      : BaseGqlTrnsWsMsg(data) { // NOLINT
    this->op_id = QUuid::fromString(data["id"].toString());
    if (this->type == PROTOCOL::ERROR) {
      errors = data.value("payload").toArray();
    }
  }

  explicit GqlTrnsWsMsgWithID(const bases::GraphQLMessage &payload,
                              const QUuid &id)
      : BaseGqlTrnsWsMsg(PROTOCOL::SUBSCRIBE, payload.serialize()),
        op_id{id} {};

  [[nodiscard]] bool has_errors() const { return !this->errors.isEmpty(); }

  [[nodiscard]] QJsonObject serialize() const override {
    QJsonObject ret = BaseGqlTrnsWsMsg::serialize();
    ret["id"] = op_id.toString();
    return ret;
  }
};

namespace DEF_MESSAGES {
const auto CONNECTION_INIT = BaseGqlTrnsWsMsg(PROTOCOL::CONNECTION_INIT);
const auto PING = BaseGqlTrnsWsMsg(PROTOCOL::PING);
const auto PONG = BaseGqlTrnsWsMsg(PROTOCOL::PONG);
} // namespace DEF_MESSAGES

struct GqlTransportWsClientSettings {
  const QUrl url;
  int ping_interval = 50000;
  int ping_timeout = 5000;
  bool auto_reconnect = false;
  int reconnect_timeout = 3000;
  std::map<QString, QString> headers = {};
};

class QTGQL_EXPORT GqlTransportWs : public QObject,
                                    public bases::NetworkLayerABC {
  Q_OBJECT

private:
  void send_message(const bases::HashAbleABC &message);

private Q_SLOTS:

  void onReconnectTimeout();

  void onPingTimeout();

  void onPingTesterTimeout();

protected:
  bool m_auto_reconnect = true;
  bool m_connection_ack = false;
  QTimer *m_reconnect_timer;
  QTimer *m_ping_timer;
  QTimer *m_ping_tester_timer;
  QWebSocket *m_ws;
  QWebSocketHandshakeOptions m_ws_options;
  GqlTransportWsClientSettings m_settings;

  std::map<QUuid, std::shared_ptr<bases::HandlerABC>> m_connected_handlers;
  // handlers that theirs execution was deferred due to connection issues.
  std::map<QUuid, std::shared_ptr<bases::HandlerABC>> m_pending_handlers;

  // general protocol handlers:
  void on_gql_ack();

  void on_gql_pong();

  void on_gql_ping();

  virtual void on_gql_next(const GqlTrnsWsMsgWithID &message);

  virtual void on_gql_error(const GqlTrnsWsMsgWithID &message);

  virtual void on_gql_complete(const GqlTrnsWsMsgWithID &message);

  void init_connection();

protected Q_SLOTS:

  virtual void onTextMessageReceived(const QString &raw_message);

  void onConnected();

  void onDisconnected();

  void onError(const QAbstractSocket::SocketError &error);
  void execute_impl(const QUuid &op_id,
                    const std::shared_ptr<bases::HandlerABC> &handler);

public:
  inline static const QString SUB_PROTOCOL = "graphql-transport-ws";

  explicit GqlTransportWs(const GqlTransportWsClientSettings &settings);

  void close(QWebSocketProtocol::CloseCode closeCode =
                 QWebSocketProtocol::CloseCodeNormal,
             const QString &reason = QString());

  [[nodiscard]] bool is_valid() const;

  // whether received connection_ack message and ws is valid.
  [[nodiscard]] bool gql_is_valid() const;

  // execute / pend a handler for execution.
  void execute(const std::shared_ptr<bases::HandlerABC> &handler,
               QUuid op_id = QUuid::createUuid()) override;
  void set_headers(const std::map<QString, QString> &headers);

  // reconnect with previous settings.
  void reconnect();
};

} // namespace qtgql::gqltransportws
