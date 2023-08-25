#include "graphql/__generated__/MainQuery.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace ScalarArgumentsTestCase {
using namespace qtgql;

auto ENV_NAME = QString("ScalarArgumentsTestCase");
auto SCHEMA_ADDR = get_server_address("ScalarArgumentsTestCase");

TEST_CASE("ScalarArgumentsTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") { REQUIRE(false); };
  SECTION("test update") { REQUIRE(false); };
}

}; // namespace ScalarArgumentsTestCase
