#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"

namespace ObjectWithListOfObjectTestCase {
using namespace qtgql;

TEST_CASE("ObjectWithListOfObjectTestCase", "[generated-testcase]") {
  auto addr = get_server_address("89749059");
  auto client =
      new DebugAbleClient(DebugClientSettings{.prod_settings = {.url = addr}});
  client->wait_for_valid();

  bases::Environment::set_gql_env(std::make_shared<bases::Environment>(
      "ObjectWithListOfObjectTestCase",
      std::unique_ptr<qtgql::gqlwstransport::GqlWsTransportClient>(client)));

  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
}

};  // namespace ObjectWithListOfObjectTestCase
