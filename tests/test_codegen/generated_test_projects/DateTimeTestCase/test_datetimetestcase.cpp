#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
namespace DateTimeTestCase {

TEST_CASE("DateTimeTestCase", "[generated-testcase]") {
  auto addr = get_server_address("24025234");
  auto client =
      new DebugAbleClient(DebugClientSettings{.prod_settings = {.url = addr}});
  client->wait_for_valid();

  qtgql::Environment::set_gql_env(std::make_shared<qtgql::Environment>(
      "DateTimeTestCase",
      std::unique_ptr<qtgql::GqlWsTransportClient>(client)));

  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  REQUIRE(QTest::qWaitFor([&]() -> bool { return mq->completed(); }, 1500));
  auto d = mq->get_data();
  auto now =
      QDateTime::currentDateTime(QTimeZone::utc()).toString("hh:mm (dd.mm.yy)");
  qDebug() << now << "vs" << d->get_birth();
  REQUIRE(d->get_birth() == now);
}

};  // namespace DateTimeTestCase