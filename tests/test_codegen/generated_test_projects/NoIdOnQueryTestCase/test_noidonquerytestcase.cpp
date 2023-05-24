#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
namespace NoIdOnQueryTestCase {
using namespace qtgql;

TEST_CASE("NoIdOnQueryTestCase", "[generated-testcase]") {
  auto addr = get_server_address("97455992");
  auto client =
      new DebugAbleClient(DebugClientSettings{.prod_settings = {.url = addr}});
  client->wait_for_valid();

  bases::Environment::set_gql_env(std::make_shared<bases::Environment>(
      "NoIdOnQueryTestCase",
      std::unique_ptr<qtgql::gqlwstransport::GqlWsTransportClient>(client)));

  auto mq = std::make_shared<mainquery::MainQuery>();
  SECTION("test appends id to query") {
    mq->fetch();
    REQUIRE(QTest::qWaitFor([&]() -> bool { return mq->completed(); }, 1500));
    REQUIRE(mq->get_data()->get_id() != bases::DEFAULTS::ID);
    REQUIRE(true);
  }
}

};  // namespace NoIdOnQueryTestCase
