#pragma once
#include <QJsonObject>
#include <QRegularExpression>
#include <QUuid>
#include <QtCore>
#include <optional>

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
  std::optional<QJsonObject> payload = {};

  QJsonObject serialize() const {
    QJsonObject data;
    data["type"] = type;
    if (payload.has_value()) {
      data["payload"] = payload.value();
    };
    return data;
  };

  BaseGqlWsTransportMessage from_json(const QJsonObject &data) {
    BaseGqlWsTransportMessage ret;
    if (data.contains("payload") && data["payload"].isObject()) {
      ret.payload = data["payload"].toObject();
    };
    if (data.contains("type") && data["type"].isString()) {
      ret.type = data["type"].toString();
    };
    return ret;
  };
};

struct GqlClientMessage : public BaseGqlWsTransportMessage {
  QUuid id = QUuid::createUuid();

  QJsonObject serialize() const {
    QJsonObject ret = BaseGqlWsTransportMessage::serialize();
    ret["id"] == id.toString();
    return ret;
  }

  GqlClientMessage from_json(const QJsonObject &data) {
    GqlClientMessage ret;
    if (data.contains("payload") && data["payload"].isObject()) {
      ret.payload = data["payload"].toObject();
    }
    if (data.contains("type") && data["type"].isString()) {
      ret.type = data["type"].toString();
    }
    ret.id = QUuid::fromString(data["id"].toString());
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
