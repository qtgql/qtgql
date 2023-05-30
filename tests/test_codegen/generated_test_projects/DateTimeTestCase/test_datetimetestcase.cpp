#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
namespace DateTimeTestCase {
using namespace qtgql;
auto ENV_NAME = QString("DateTimeTestCase");
auto SCHEMA_ADDR = get_server_address("24025234");

TEST_CASE("DateTimeTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  auto d = mq->get_data();
  auto now = QDateTime::currentDateTime(QTimeZone::utc())
                 .toString("hh:mm (dd.mm.yyyy)");
  REQUIRE(d->get_birth() == now);
}

};  // namespace DateTimeTestCase
