#include "gqloverhttp.hpp"

#include <utility>

namespace qtgql::gqloverhttp {

PostQueryMessage::PostQueryMessage(QString _query,
                                   std::optional<QJsonObject> vars)
    : query{std::move(_query)}, variables{std::move(vars)} {
  auto op_name = utils::get_operation_name(query);
  Q_ASSERT_X(op_name.has_value(), "OperationPayload",
             "qtgql enforces operations to have names your query has no "
             "operation name");
  operationName = op_name.value();
}

QJsonObject PostQueryMessage::serialize() const {
  QJsonObject ret{{"operationName", operationName}, {"query", query}};
  if (variables.has_value()) {
    ret.insert("variables", variables.value());
  }
  return ret;
}

GraphQLResponse::GraphQLResponse(const QJsonObject &payload) {
  // with the new rfc, valid responses must return data that is not null.
  // https://github.com/graphql/graphql-over-http/blame/d312e43384006fa323b918d49cfd9fbd76ac1257/spec/GraphQLOverHTTP.md#L630-L632
  // this is here due to backward compat until 2025
  if (!payload.value("data").isNull()) {
    data = payload.value("data").toObject();
  }
  if (!payload.value("errors").isNull()) {
    errors = payload.value("errors").toArray();
  }
}

} // namespace qtgql::gqloverhttp
