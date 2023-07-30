#include "graphql/__generated__/ChangeName.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace FragmentWithOperationVariable {
using namespace qtgql;

auto ENV_NAME = QString("FragmentWithOperationVariable");
auto SCHEMA_ADDR = get_server_address("FragmentWithOperationVariable");

TEST_CASE("FragmentWithOperationVariable", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  auto mq = mainquery::MainQuery::shared();
  SECTION("test deserialize") {
    SECTION("when null returns default values") {
      mq->set_variables({true});
      mq->fetch();
      test_utils::wait_for_completion(mq);
      auto user = mq->data()->get_user();
      REQUIRE(user->get_age() == bases::DEFAULTS::INT);
      REQUIRE(user->get_name() == bases::DEFAULTS::STRING);
      REQUIRE(user->get_agePoint() == bases::DEFAULTS::FLOAT);
      REQUIRE(user->get_uuid() == bases::DEFAULTS::UUID);
      REQUIRE(user->get_birth() ==
              qtgql::customscalars::DateTimeScalar().to_qt());
    };
    SECTION("when not null") {
      mq->set_variables({false});
      mq->fetch();
      test_utils::wait_for_completion(mq);
      auto user = mq->data()->get_user();
      REQUIRE(user->get_age() != bases::DEFAULTS::INT);
      REQUIRE(user->get_name() != bases::DEFAULTS::STRING);
      REQUIRE(user->get_agePoint() != bases::DEFAULTS::FLOAT);
      REQUIRE(user->get_uuid() != bases::DEFAULTS::UUID);
      REQUIRE(user->get_birth() !=
              qtgql::customscalars::DateTimeScalar().to_qt());
    }
  }

  SECTION("test updates") {
    mq->set_variables({true});
    mq->fetch();
    test_utils::wait_for_completion(mq);
    auto change_name_mutation = changename::ChangeName::shared();
    QString new_name = "Moise";
    auto user = mq->data()->get_user();
    change_name_mutation->set_variables({user->get_id(), new_name});
    auto catcher = test_utils::SignalCatcher({user});
    change_name_mutation->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(change_name_mutation);
    REQUIRE(user->get_name() == "Moise");
  };
}

}; // namespace FragmentWithOperationVariable
