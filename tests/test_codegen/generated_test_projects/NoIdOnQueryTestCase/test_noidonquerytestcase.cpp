#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
namespace NoIdOnQueryTestCase {
using namespace qtgql;
auto ENV_NAME = QString("NoIdOnQueryTestCase");
auto SCHEMA_ADDR = get_server_address("76177312");

TEST_CASE("NoIdOnQueryTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize and appends ID selection to query") {
    REQUIRE(mq->data()->get_user()->get_id() != bases::DEFAULTS::ID);
  }
}

}; // namespace NoIdOnQueryTestCase
