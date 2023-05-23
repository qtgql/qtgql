#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
namespace DateTimeTestCase {

TEST_CASE("DateTimeTestCase", "[generated-testcase]") {
  auto addr = get_server_address("24025234");
  auto client =
      new DebugAbleClient(DebugClientSettings{.prod_settings = {.url = addr}});
  client->wait_for_valid();

  qtgql::Environment::set_gql_env(std::make_shared<qtgql::Environment>(
      "DateTimeTestCase",
      std::unique_ptr<qtgql::GqlWsTransportClient>(client)));

  REQUIRE(false);
}

};  // namespace DateTimeTestCase
