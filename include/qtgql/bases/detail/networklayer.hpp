/*
 * Encapsulates the API which will be used by the codegen
 * currently the only implementation is with graphql-ws-transport protocol
 * at ../gqlwstransport dir.
 */
#pragma once

#include "QJsonObject"
#include "QUuid"
#include "exceptions.hpp"
#include "qtgql/utils.hpp"
#include <QJsonArray>
#include <QJsonDocument>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QNetworkRequest>
#include <QString>
#include <optional>
#include <utility>

namespace qtgql::bases {

struct HashAbleABC {
  [[nodiscard]] virtual QJsonObject serialize() const {
    throw exceptions::NotImplementedError({});
  };
};

struct GraphQLMessage : public bases::HashAbleABC {
  QString query;
  QString operationName;
  std::optional<QJsonObject> variables;

  explicit GraphQLMessage(QString _query, std::optional<QJsonObject> vars = {})
      : query{std::move(_query)}, variables{std::move(vars)} {
    auto op_name = utils::get_operation_name(query);
    Q_ASSERT_X(op_name.has_value(), "OperationPayload",
               "qtgql enforces operations to have names your query has no "
               "operation name");
    operationName = op_name.value();
  }

  [[nodiscard]] QJsonObject serialize() const override {
    QJsonObject ret{{"operationName", operationName}, {"query", query}};
    if (variables.has_value()) {
      ret.insert("variables", variables.value());
    }
    return ret;
  };
  void set_variables(const QJsonObject &vars) { variables = vars; }
};

struct HandlerABC {

  // this is mainly for graphql-ws-transport.
  QUuid id;

  // https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md#next
  virtual void on_next(const QJsonObject &message) = 0;

  // https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md#error
  virtual void on_error(const QJsonArray &errors) = 0;

  // https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md#complete
  virtual void on_completed() = 0;

  virtual const GraphQLMessage &message() = 0;
};

/*
class that should  support executing handlers
 and expected to call the handler's `on_data` /
`on_error` / 'on_completed' when the operation is completed.
*/
struct NetworkLayerABC {
  virtual void execute(const std::shared_ptr<HandlerABC> &handler) {
    throw exceptions::NotImplementedError({});
  }
};

} // namespace qtgql::bases
