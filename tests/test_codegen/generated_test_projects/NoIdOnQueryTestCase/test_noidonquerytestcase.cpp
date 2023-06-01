#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
namespace NoIdOnQueryTestCase {
using namespace qtgql;
auto ENV_NAME = QString("NoIdOnQueryTestCase");
auto SCHEMA_ADDR = get_server_address("39238999");

TEST_CASE("NoIdOnQueryTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  SECTION("test appends id to query") {
    mq->fetch();
    REQUIRE(QTest::qWaitFor([&]() -> bool { return mq->completed(); }, 1500));
    REQUIRE(mq->get_data()->get_id() != bases::DEFAULTS::ID);
    REQUIRE(true);
  }
}

};  // namespace NoIdOnQueryTestCase
