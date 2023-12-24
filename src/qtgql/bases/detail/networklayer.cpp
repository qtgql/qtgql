#include "networklayer.hpp"
namespace qtgql::bases {

void NetworkLayerABC::execute(const std::shared_ptr<HandlerABC> &handler,
                              QUuid op_id) {
  throw exceptions::NotImplementedError({});
}

GraphQLMessage::GraphQLMessage(QString _query, std::optional<QJsonObject> vars)
    : query{std::move(_query)}, variables{std::move(vars)} {
  auto op_name = get_operation_name(query);
  Q_ASSERT_X(op_name.has_value(), "OperationPayload",
             "qtgql enforces operations to have names your query has no "
             "operation name");
  operationName = op_name.value();
}

QJsonObject GraphQLMessage::serialize() const {
  QJsonObject ret{{"operationName", operationName}, {"query", query}};
  if (variables.has_value()) {
    ret.insert("variables", variables.value());
  }
  return ret;
}

void GraphQLMessage::set_variables(const QJsonObject &vars) {
  variables = vars;
}

std::optional<QString> get_operation_name(const QString &query) {
  static QRegularExpression re(
      "(subscription|mutation|query)( [0-9a-zA-Z_]+)*");
  auto match = re.match(query);
  if (match.hasMatch()) {
    return match.captured(2).trimmed();
  }
  return {};
}
} // namespace qtgql::bases
