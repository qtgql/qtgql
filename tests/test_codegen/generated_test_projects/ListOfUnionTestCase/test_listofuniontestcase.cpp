#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace ListOfUnionTestCase {
using namespace qtgql;

auto ENV_NAME = QString("ListOfUnionTestCase");
auto SCHEMA_ADDR = get_server_address("70862812");

TEST_CASE("ListOfUnionTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") { REQUIRE(false); };
  SECTION("test update") { REQUIRE(false); };
}

}; // namespace ListOfUnionTestCase
