#include "routers.hpp"

qtgql::routers::SubscriptionRouter::SubscriptionRouter(
    std::shared_ptr<gqltransportws::GqlTransportWs> ws_layer,
    std::shared_ptr<gqloverhttp::GraphQLOverHttp> http_layer)
    : ws_layer(std::move(ws_layer)), http_layer(std::move(http_layer)) {}

void qtgql::routers::SubscriptionRouter::execute(
    const std::shared_ptr<bases::HandlerABC> &handler, QUuid op_id) {
  auto message = handler->message();
  if (message.query.startsWith("subscription")) {
    ws_layer->execute(handler, op_id);
  } else {
    http_layer->execute(handler, op_id);
  }
}
