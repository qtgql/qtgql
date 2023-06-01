#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"

namespace DateTestCase {
using namespace qtgql;
auto ENV_NAME = QString("DateTestCase");
auto SCHEMA_ADDR = get_server_address("35700974");
TEST_CASE("DateTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.print_debug = false,
                                    .prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  auto d = mq->get_data();
  auto now = QDate::currentDate().toString("dd.MM.yyyy");
  REQUIRE(d->get_birth() == now);
}

};  // namespace DateTestCase
