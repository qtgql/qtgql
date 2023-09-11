#include "gen/MainQuery.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace UnionWithNodeTestCase {
using namespace qtgql;

auto ENV_NAME = std::string("UnionWithNodeTestCase");
auto SCHEMA_ADDR = get_server_address("8601306");

TEST_CASE("UnionWithNodeTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") { REQUIRE(false); };
  SECTION("test update") { REQUIRE(false); };
}

}; // namespace UnionWithNodeTestCase
