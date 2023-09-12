#include <QSignalSpy>
#include <QTest>
#include "testframework.hpp"

#include "gen/FillUser.hpp"
#include "gen/MainQuery.hpp"
#include "gen/NullifyUser.hpp"
#include "testutils.hpp"

namespace OptionalScalars {
using namespace qtgql;
auto ENV_NAME = std::string("OptionalScalars");
auto SCHEMA_ADDR = get_server_address(QString::fromStdString(ENV_NAME));

template <typename User> void check_user_is_nulled(const User &user) {
  REQUIRE(user->get_age() == bases::DEFAULTS::INT);
  REQUIRE(user->get_name() == bases::DEFAULTS::STRING);
  REQUIRE(user->get_agePoint() == bases::DEFAULTS::FLOAT);
  REQUIRE(user->get_uuid() == bases::DEFAULTS::UUID);
  REQUIRE(user->get_birth() == qtgql::customscalars::DateTimeScalar().to_qt());
}

template <typename User> void check_user_filled(const User &user) {
  REQUIRE(user->get_age() != bases::DEFAULTS::INT);
  REQUIRE(user->get_name() != bases::DEFAULTS::STRING);
  REQUIRE(user->get_agePoint() != bases::DEFAULTS::FLOAT);
  REQUIRE(user->get_uuid() != bases::DEFAULTS::UUID);
  REQUIRE(user->get_birth() != qtgql::customscalars::DateTimeScalar().to_qt());
}

TEST_CASE("OptionalScalars") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = mainquery::MainQuery::shared();
  SECTION("test deserialize - when null returns default values") {
    mq->set_variables({true});
    mq->fetch();
    test_utils::wait_for_completion(mq);
    auto user = mq->data()->get_user();
    check_user_is_nulled(user);
  };
  SECTION("test deserialize - when not null") {
    mq->set_variables({false});
    mq->fetch();
    test_utils::wait_for_completion(mq);
    auto user = mq->data()->get_user();
    check_user_filled(user);
  }

  SECTION("test updates - from null to value") {
    mq->set_variables({true});
    mq->fetch();
    test_utils::wait_for_completion(mq);
    auto change_name_mutation = filluser::FillUser::shared();
    auto user = mq->data()->get_user();
    check_user_is_nulled(user);
    change_name_mutation->set_variables({user->get_id()});
    auto catcher = test_utils::SignalCatcher({user});
    change_name_mutation->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(change_name_mutation);
    check_user_filled(user);
  };
  SECTION("test update - from value to null") {
    mq->set_variables({false});
    mq->fetch();
    test_utils::wait_for_completion(mq);
    auto user = mq->data()->get_user();
    check_user_filled(user);
    auto catcher = test_utils::SignalCatcher({user});

    auto nullify_mut = nullifyuser::NullifyUser::shared();
    nullify_mut->set_variables({mq->data()->get_user()->get_id()});
    nullify_mut->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(nullify_mut);
    check_user_is_nulled(user);
  }
}

}; // namespace OptionalScalarsTestCase
