#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
namespace OptionalScalarsTestCase {

TEST_CASE("OptionalScalarsTestCase", "[generated-testcase]") {
  auto addr = get_server_address("56413013");
  auto client =
      new DebugAbleClient(DebugClientSettings{.prod_settings = {.url = addr}});
  client->wait_for_valid();

  qtgql::Environment::set_gql_env(std::make_shared<qtgql::Environment>(
      "OptionalScalarsTestCase",
      std::unique_ptr<qtgql::GqlWsTransportClient>(client)));
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  SECTION("test scalar types and deserialization") {
    REQUIRE(QTest::qWaitFor([&]() -> bool { return mq->completed(); }, 1500));
    auto d = mq->get_data();
    REQUIRE(d->get_age() == qtgql::DEFAULTS::INT);
    REQUIRE(d->get_id() == "FakeID");
    REQUIRE(d->get_name() == qtgql::DEFAULTS::STRING);
  };
}

};  // namespace OptionalScalarsTestCase
