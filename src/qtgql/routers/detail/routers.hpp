#pragma once
#include "qtgql/bases/bases.hpp"
#include "qtgql/gqloverhttp/gqloverhttp.hpp"
#include "qtgql/gqltransportws/gqltransportws.hpp"
#include "qtgql/qtgql_export.hpp"

namespace qtgql::routers {

/* routes subscriptions to gql-ws-transport and other operations to
 graphql-over-http.
 */
class QTGQL_EXPORT SubscriptionRouter : public bases::NetworkLayerABC {
  std::shared_ptr<gqltransportws::GqlTransportWs> ws_layer;
  std::shared_ptr<gqloverhttp::GraphQLOverHttp> http_layer;

public:
  explicit SubscriptionRouter(
      std::shared_ptr<gqltransportws::GqlTransportWs> ws_layer,
      std::shared_ptr<gqloverhttp::GraphQLOverHttp> http_layer);

  void execute(const std::shared_ptr<bases::HandlerABC> &handler,
               QUuid op_id = QUuid::createUuid()) override;
};

} // namespace qtgql::routers
