#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
namespace DateTimeTestCase {
using namespace qtgql;
TEST_CASE("DateTimeTestCase", "[generated-testcase]") {
  auto addr = get_server_address("24025234");
  auto client =
      new DebugAbleClient(DebugClientSettings{.prod_settings = {.url = addr}});
  client->wait_for_valid();

  bases::Environment::set_gql_env(std::make_shared<bases::Environment>(
      "DateTimeTestCase",
      std::unique_ptr<qtgql::gqlwstransport::GqlWsTransportClient>(client)));

  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  REQUIRE(QTest::qWaitFor([&]() -> bool { return mq->completed(); }, 1500));
  auto d = mq->get_data();
  auto now = QDateTime::currentDateTime(QTimeZone::utc())
                 .toString("hh:mm (dd.mm.yyyy)");
  REQUIRE(d->get_birth() == now);
}

};  // namespace DateTimeTestCase
