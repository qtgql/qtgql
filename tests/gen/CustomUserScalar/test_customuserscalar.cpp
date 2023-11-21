#include "testframework.hpp"
#include "testutils.hpp"

namespace CustomUserScalar {
using namespace qtgql;

auto ENV_NAME = std::string("CustomUserScalar");
auto SCHEMA_ADDR =
    test_utils::get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("CustomUserScalar") {
  test_utils::get_or_create_env(
      ENV_NAME,
      test_utils::DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") { REQUIRE(false); };
  SECTION("test update") { REQUIRE(false); };
}

}; // namespace CustomUserScalar
