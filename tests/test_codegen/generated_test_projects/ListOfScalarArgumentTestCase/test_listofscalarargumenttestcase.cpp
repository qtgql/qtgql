#include "graphql/__generated__/EchoArg.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>
namespace ListOfScalarArgumentTestCase {
using namespace qtgql;

auto ENV_NAME = QString("ListOfScalarArgumentTestCase");
auto SCHEMA_ADDR = get_server_address("ListOfScalarArgumentTestCase");

TEST_CASE("ListOfScalarArgumentTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") { REQUIRE(false); };
  SECTION("test update") { REQUIRE(false); };
}

}; // namespace ListOfScalarArgumentTestCase
