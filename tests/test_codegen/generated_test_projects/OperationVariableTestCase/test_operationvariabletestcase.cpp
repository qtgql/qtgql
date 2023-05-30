#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"

namespace OperationVariableTestCase {
using namespace qtgql;

auto ENV_NAME = QString("OperationVariableTestCase");
auto SCHEMA_ADDR = get_server_address("5881041");

TEST_CASE("OperationVariableTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  REQUIRE(false);
}

};  // namespace OperationVariableTestCase
