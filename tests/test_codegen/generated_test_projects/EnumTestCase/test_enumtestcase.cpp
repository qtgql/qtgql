#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"

namespace EnumTestCase {
using namespace qtgql;

auto ENV_NAME = QString("EnumTestCase");
auto SCHEMA_ADDR = get_server_address("60114840");

TEST_CASE("EnumTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  SECTION("test deserialize") {
    test_utils::wait_for_completion(mq);
    REQUIRE(mq->get_data()->get_status() == EnumTestCase::Enums::Connected);
  }
}

}; // namespace EnumTestCase
