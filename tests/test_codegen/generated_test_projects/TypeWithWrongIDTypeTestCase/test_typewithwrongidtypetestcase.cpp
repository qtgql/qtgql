#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"

TEST_CASE("TypeWithWrongIDTypeTestCase") {
  auto addr = get_server_address("97455992");
  auto client = new DebugAbleClient({.prod_settings = {.url = addr}});
  client->wait_for_valid();

  qtgql::QtGqlEnvironment::set_gql_env(
      std::make_shared<qtgql::QtGqlEnvironment>(
          "TypeWithWrongIDTypeTestCase",
          std::unique_ptr<qtgql::GqlWsTransportClient>(client)));

  REQUIRE(false);
}
