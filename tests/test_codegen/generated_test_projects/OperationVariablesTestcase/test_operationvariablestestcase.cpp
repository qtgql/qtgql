#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace OperationVariablesTestcase {
using namespace qtgql;

auto ENV_NAME = QString("OperationVariablesTestcase");
auto SCHEMA_ADDR = get_server_address("81695428");

TEST_CASE("OperationVariablesTestcase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = mainquery::MainQuery::shared();
  mq->fetch();
  test_utils::wait_for_completion(mq);

  SECTION("test deserialize") {
    REQUIRE(!mq->get_data()->get_name().isEmpty());
    REQUIRE(!mq->get_data()->get_friend()->get_name().isEmpty());
  };
  SECTION("test update") { REQUIRE(false); };
}

}; // namespace OperationVariablesTestcase
