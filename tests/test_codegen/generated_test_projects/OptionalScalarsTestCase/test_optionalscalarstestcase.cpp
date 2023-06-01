#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
namespace OptionalScalarsTestCase {
using namespace qtgql;
auto ENV_NAME = QString("OptionalScalarsTestCase");
auto SCHEMA_ADDR = get_server_address("15332448");

TEST_CASE("OptionalScalarsTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();

  SECTION("when null returns default values") {
    mq->set_variables({true});
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
    mq->set_variables({false});
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
