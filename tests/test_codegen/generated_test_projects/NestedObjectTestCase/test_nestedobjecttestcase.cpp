#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
namespace NestedObjectTestCase {
using namespace qtgql;

TEST_CASE("NestedObjectTestCase", "[generated-testcase]") {
  auto addr = get_server_address("26433428");
  auto client =
      new DebugAbleClient(DebugClientSettings{.prod_settings = {.url = addr}});
  client->wait_for_valid();

  bases::Environment::set_gql_env(std::make_shared<bases::Environment>(
      "NestedObjectTestCase",
      std::unique_ptr<qtgql::gqlwstransport::GqlWsTransportClient>(client)));

  REQUIRE(false);
}

};  // namespace NestedObjectTestCase
