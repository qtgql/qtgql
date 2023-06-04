#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"

namespace TimeScalarTestCase {
using namespace qtgql;
auto ENV_NAME = QString("TimeScalarTestCase");
auto SCHEMA_ADDR = get_server_address("18142566");

TEST_CASE("TimeScalarTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    auto d = mq->get_data();
    auto now = QDateTime::currentDateTime(QTimeZone::utc()).time().toString();
    REQUIRE(d->get_whatTimeIsIt() == now);
  }
}

};  // namespace TimeScalarTestCase
