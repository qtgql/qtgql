#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"

TEST_CASE("ScalarsTestCase", "[generated-testcase]") {
  auto addr = get_server_address("97455992");
  auto client = new DebugAbleClient(
      {.print_debug = false, .prod_settings = {.url = addr}});
  client->wait_for_valid();
  qtgql::QtGqlEnvironment::set_gql_env(
      std::make_shared<qtgql::QtGqlEnvironment>(
          "ScalarsTestCase",
          std::unique_ptr<qtgql::GqlWsTransportClient>(client)));

  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  SECTION("test scalar types and deserialization") {
    REQUIRE(QTest::qWaitFor([&]() -> bool { return mq->completed(); }, 1500));
    auto d = mq->get_data();
    REQUIRE(d->get_age() == 24);
    REQUIRE(d->get_agePoint() == 24.0f);
    REQUIRE(d->get_id() == "FakeID");
    REQUIRE(d->get_male() == true);
    REQUIRE(d->get_name() == "nir");
    REQUIRE(d->get_uuid() ==
            QUuid::fromString("06335e84-2872-4914-8c5d-3ed07d2a2f16\""));
  }
}
