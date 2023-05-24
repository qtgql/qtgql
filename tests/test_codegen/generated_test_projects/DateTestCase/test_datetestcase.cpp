#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"

namespace DateTestCase {
using namespace qtgql;

TEST_CASE("DateTestCase", "[generated-testcase]") {
  auto addr = get_server_address("35700974");
  auto client =
      new DebugAbleClient(DebugClientSettings{.prod_settings = {.url = addr}});
  client->wait_for_valid();

  bases::Environment::set_gql_env(std::make_shared<bases::Environment>(
      "DateTestCase",
      std::unique_ptr<gqlwstransport::GqlWsTransportClient>(client)));

  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  REQUIRE(QTest::qWaitFor([&]() -> bool { return mq->completed(); }, 1500));
  auto d = mq->get_data();
  auto now = QDate::currentDate().toString("dd.MM.yyyy");
  REQUIRE(d->get_birth() == now);
}

};  // namespace DateTestCase
