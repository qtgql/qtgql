#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
namespace DecimalTestCase {
using namespace qtgql;
auto ENV_NAME = QString("DecimalTestCase");
auto SCHEMA_ADDR = get_server_address("91812902");

TEST_CASE("DecimalTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  REQUIRE(QTest::qWaitFor([&]() -> bool { return mq->completed(); }, 1500));
  REQUIRE(!mq->get_data()->get_balance().isEmpty());
}

};  // namespace DecimalTestCase
