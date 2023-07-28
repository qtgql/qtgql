#pragma once
#include "qtgql/bases/bases.hpp"
#include "qtgql/gqloverhttp/gqloverhttp.hpp"
#include "qtgql/gqlwstransport/gqlwstransport.hpp"

namespace qtgql::routers {

// routes subscriptions to gql-ws-transport and other operations to
// graphql-over-http.
class SubscriptionRouter : public bases::NetworkLayerABC {
  std::unique_ptr<gqlwstransport::GqlWsTransport> ws_layer;
  std::unique_ptr<gqloverhttp::GraphQLOverHttp> http_layer;

  inline void execute(const std::shared_ptr<bases::HandlerABC> &handler) final {
    auto message = handler->message();
    if (message.query.startsWith("subscription")) {
      ws_layer->execute(handler);
    } else {
      http_layer->execute(handler);
    }
  }
};

} // namespace qtgql::routers
