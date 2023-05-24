#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
namespace DecimalTestCase {
using namespace qtgql;

TEST_CASE("DecimalTestCase", "[generated-testcase]") {
  auto addr = get_server_address("91812902");
  auto client =
      new DebugAbleClient(DebugClientSettings{.prod_settings = {.url = addr}});
  client->wait_for_valid();

  bases::Environment::set_gql_env(std::make_shared<bases::Environment>(
      "DecimalTestCase", std::unique_ptr<qtgql::GqlWsTransportClient>(client)));

  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  REQUIRE(QTest::qWaitFor([&]() -> bool { return mq->completed(); }, 1500));
  REQUIRE(!mq->get_data()->get_balance().isEmpty());
}

};  // namespace DecimalTestCase
