#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
namespace OptionalScalarsTestCase {
using namespace qtgql;
TEST_CASE("OptionalScalarsTestCase", "[generated-testcase]") {
  auto addr = get_server_address("15332448");
  auto client =
      new DebugAbleClient(DebugClientSettings{.prod_settings = {.url = addr}});
  client->wait_for_valid();

  bases::Environment::set_gql_env(std::make_shared<bases::Environment>(
      "OptionalScalarsTestCase",
      std::unique_ptr<gqlwstransport::GqlWsTransportClient>(client)));
  auto mq = std::make_shared<mainquery::MainQuery>();

  SECTION("when null returns default values") {
    mq->setVariables({true});
    mq->fetch();
    test_utils::wait_for_completion(mq);
    auto d = mq->get_data();
    REQUIRE(d->get_age() == bases::DEFAULTS::INT);
    REQUIRE(d->get_name() == bases::DEFAULTS::STRING);
    REQUIRE(d->get_agePoint() == bases::DEFAULTS::FLOAT);
    REQUIRE(d->get_uuid() == bases::DEFAULTS::UUID);
    REQUIRE(d->get_birth() == qtgql::customscalars::DateTimeScalar().to_qt());
  };
  SECTION("when not null") {
    mq->setVariables({false});
    mq->fetch();
    test_utils::wait_for_completion(mq);
    auto d = mq->get_data();
    REQUIRE(d->get_age() != bases::DEFAULTS::INT);
    REQUIRE(d->get_name() != bases::DEFAULTS::STRING);
    REQUIRE(d->get_agePoint() != bases::DEFAULTS::FLOAT);
    REQUIRE(d->get_uuid() != bases::DEFAULTS::UUID);
    REQUIRE(d->get_birth() != qtgql::customscalars::DateTimeScalar().to_qt());
  }
}

};  // namespace OptionalScalarsTestCase
