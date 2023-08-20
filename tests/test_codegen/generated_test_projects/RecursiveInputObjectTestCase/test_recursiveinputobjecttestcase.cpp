#include "graphql/__generated__/MainQuery.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace RecursiveInputObjectTestCase {
using namespace qtgql;

auto ENV_NAME = QString("RecursiveInputObjectTestCase");
auto SCHEMA_ADDR = get_server_address("RecursiveInputObjectTestCase");

TEST_CASE("RecursiveInputObjectTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") { REQUIRE(false); };
  SECTION("test update") { REQUIRE(false); };
}

}; // namespace RecursiveInputObjectTestCase
