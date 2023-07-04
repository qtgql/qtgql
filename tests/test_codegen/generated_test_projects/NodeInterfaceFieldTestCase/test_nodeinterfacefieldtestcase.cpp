#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace NodeInterfaceFieldTestCase {
using namespace qtgql;

auto ENV_NAME = QString("NodeInterfaceFieldTestCase");
auto SCHEMA_ADDR = get_server_address("146984");

TEST_CASE("NodeInterfaceFieldTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = mainquery::MainQuery::shared();
  mq->set_variables({NodeInterfaceFieldTestCase::Enums::TypesEnum::User});
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    REQUIRE(mq->data()->get_node()->__typename() == "User");
  };
  SECTION("test update") { REQUIRE(false); };
}

}; // namespace NodeInterfaceFieldTestCase
