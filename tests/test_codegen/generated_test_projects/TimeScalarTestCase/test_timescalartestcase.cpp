#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"

namespace TimeScalarTestCase {
using namespace qtgql;

TEST_CASE("TimeScalarTestCase", "[generated-testcase]") {
  auto addr = get_server_address("18142566");
  auto client =
      new DebugAbleClient(DebugClientSettings{.prod_settings = {.url = addr}});
  client->wait_for_valid();

  bases::Environment::set_gql_env(std::make_shared<bases::Environment>(
      "TimeScalarTestCase",
      std::unique_ptr<qtgql::GqlWsTransportClient>(client)));
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  REQUIRE(QTest::qWaitFor([&]() -> bool { return mq->completed(); }, 1500));
  auto d = mq->get_data();
  auto now = QDateTime::currentDateTime(QTimeZone::utc()).time().toString();
  REQUIRE(d->get_whatTimeIsIt() == now);
}

};  // namespace TimeScalarTestCase
