/*
 * Encapsulates the API which will be used by the codegen
 * currently the only implementation is with graphql-ws-transport protocol
 * at ../gqlwstransport dir.
 */
#pragma once
#include "QJsonObject"
#include "QUuid"
#include "exceptions.hpp"
#include "qtgql/qtgql_export.hpp"
#include <QJsonArray>
#include <QJsonDocument>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QRegularExpression>
#include <QString>
#include <optional>
#include <utility>

namespace qtgql::bases {
QTGQL_EXPORT std::optional<QString> get_operation_name(const QString &query);

struct HashAbleABC {
  [[nodiscard]] virtual QJsonObject serialize() const {
    throw exceptions::NotImplementedError({});
  };
};

struct QTGQL_EXPORT GraphQLMessage : public bases::HashAbleABC {
  QString query;
  QString operationName;
  std::optional<QJsonObject> variables;

  explicit GraphQLMessage(QString _query, std::optional<QJsonObject> vars = {});

  [[nodiscard]] QJsonObject serialize() const override;
  void set_variables(const QJsonObject &vars);
};

struct QTGQL_EXPORT HandlerABC {

  // https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md#next
  virtual void on_next(const QJsonObject &message) = 0;

  // https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md#error
  virtual void on_error(const QJsonArray &errors) = 0;

  // https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md#complete
  virtual void on_completed() = 0;

  virtual const GraphQLMessage &message() = 0;
};

/*
class that should support executing handlers
 and expected to call the handler's `on_data` /
`on_error` / 'on_completed' when the operation is completed.
*/
struct QTGQL_EXPORT NetworkLayerABC {
  virtual void execute(const std::shared_ptr<HandlerABC> &handler,
                       QUuid op_id = QUuid::createUuid());
};

} // namespace qtgql::bases
