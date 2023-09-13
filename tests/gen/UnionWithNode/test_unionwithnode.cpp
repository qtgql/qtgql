#include "gen/MainQuery.hpp"
#include "testframework.hpp"
#include "testutils.hpp"
#include <QSignalSpy>

namespace UnionWithNode {
using namespace qtgql;

auto ENV_NAME = std::string("UnionWithNode");
auto SCHEMA_ADDR = get_server_address("8601306");

TEST_CASE("UnionWithNode") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") { REQUIRE(false); };
  SECTION("test update") { REQUIRE(false); };
}

}; // namespace UnionWithNode
