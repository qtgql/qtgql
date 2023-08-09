#include "graphql/__generated__/HelloOrEchoQuery.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace OptionalInputTestCase {
using namespace qtgql;

auto ENV_NAME = QString("OptionalInputTestCase");
auto SCHEMA_ADDR = get_server_address("OptionalInputTestCase");

TEST_CASE("OptionalInputTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") { REQUIRE(false); };
  SECTION("test update") { REQUIRE(false); };
}

}; // namespace OptionalInputTestCase
