#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/ChangeName.hpp"
#include "graphql/__generated__/MainQuery.hpp"

namespace OptionalScalarsTestCase {
using namespace qtgql;
auto ENV_NAME = QString("OptionalScalarsTestCase");
auto SCHEMA_ADDR = get_server_address("65545288");

TEST_CASE("OptionalScalarsTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  SECTION("test deserialize") {
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
  mq->set_variables({true});
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test updates") {
    auto change_name_mutation = changename::ChangeName::shared();
    QString new_name = "Moise";
    change_name_mutation->set_variables(mq->get_data()->get_id(), new_name);
    auto catcher = test_utils::SignalCatcher({mq->get_data()});
    change_name_mutation->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(change_name_mutation);
    REQUIRE(mq->get_data()->get_name() == "Moise");
  };
}

}; // namespace OptionalScalarsTestCase
