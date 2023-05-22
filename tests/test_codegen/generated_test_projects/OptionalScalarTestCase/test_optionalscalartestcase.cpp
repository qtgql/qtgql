#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
namespace OptionalScalarTestCase {

TEST_CASE("OptionalScalarTestCase", "[generated-testcase]") {
  auto addr = get_server_address("82130731");
  auto client =
      new DebugAbleClient(DebugClientSettings{.prod_settings = {.url = addr}});
  client->wait_for_valid();

  qtgql::QtGqlEnvironment::set_gql_env(
      std::make_shared<qtgql::QtGqlEnvironment>(
          "OptionalScalarTestCase",
          std::unique_ptr<qtgql::GqlWsTransportClient>(client)));

  REQUIRE(false);
}

};  // namespace OptionalScalarTestCase
