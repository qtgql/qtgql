#pragma once
#include "qtgql/bases/bases.hpp"
#include "qtgql/qtgql_export.hpp"
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>

#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QString>
#include <QUuid>
#include <optional>

// Implementation of the GrapQL over HTTP protocol
// https://graphql.github.io/graphql-over-http/draft/

namespace qtgql::gqloverhttp {

struct GraphQLResponse {
  std::optional<QJsonObject> data = {};
  std::optional<QJsonArray> errors = {};

  GraphQLResponse() = delete;

  explicit GraphQLResponse(const QJsonObject &payload);
};

// For mutations, you have to use POST and send json, for queries it is
// optional. We use POST and json always for simplicity.
inline const QByteArray HTTP_CONTENT_TYPE = "application/json";
inline const QByteArray HTTP_ACCEPT = "application/graphql-response+json";

class _GraphQLRequest : public QNetworkRequest {

public:
  _GraphQLRequest(const QUrl &url,
                  const std::list<std::pair<QByteArray, QByteArray>> &headers)
      : QNetworkRequest(url) {
    for (auto &header : headers) {
      setRawHeader(header.first, header.second);
    }
    setRawHeader("Accept", HTTP_ACCEPT);
    setRawHeader("Content-Type", HTTP_CONTENT_TYPE);
  }
};

class QTGQL_EXPORT GraphQLOverHttp : public QObject,
                                     public bases::NetworkLayerABC {
  Q_OBJECT
protected:
  QUrl m_url;
  QUuid op_uuid;
  std::unique_ptr<QNetworkAccessManager> m_manager;
  std::list<std::pair<QByteArray, QByteArray>> m_headers = {};

public:
  explicit GraphQLOverHttp(
      QUrl url, const std::map<std::string, std::string> &headers = {})
      : QObject::QObject(nullptr), m_url(std::move(url)) {
    set_headers(headers);
    m_manager = std::make_unique<QNetworkAccessManager>();
  }
  inline void set_headers(const std::map<std::string, std::string> &headers) {
    m_headers.clear();
    for (const auto &kv : headers) {
      m_headers.emplace_front(QByteArray::fromStdString(kv.first),
                              QByteArray::fromStdString(kv.second));
    }
  }

  // execute a handler for execution.
  void execute(const std::shared_ptr<bases::HandlerABC> &handler,
               QUuid op_id = QUuid::createUuid()) override {
    op_uuid = op_id;
    QJsonDocument data(handler->message().serialize());
    auto reply = m_manager->post(_GraphQLRequest(m_url, m_headers),
                                 QByteArray(data.toJson()));
    reply->setProperty("uuid", op_uuid);
    QObject::connect(reply, &QNetworkReply::finished, [=]() {
      if (reply->error() == QNetworkReply::NoError) {
        process_reply(reply, op_uuid, handler);
      } else {
        qWarning() << reply->errorString();
      }
      reply->deleteLater();
    });
  };
  static void process_reply(QNetworkReply *reply, QUuid uuid,
                            const std::shared_ptr<bases::HandlerABC> &handler) {
    if (uuid == reply->property("uuid")) {
      auto raw_data = reply->readAll();
      auto response =
          GraphQLResponse(QJsonDocument::fromJson(raw_data).object());
      if (response.errors.has_value()) {
        handler->on_error(response.errors.value());
      };
      if (response.data.has_value()) {
        handler->on_next(response.data.value());
      }
    } else {
      handler->on_error(QJsonArray(
          {"Uuid of reply is different with uuid of current request"}));
    }
    // Http over GraphQL has only one response per request.
    handler->on_completed();
  };
};

} // namespace qtgql::gqloverhttp
