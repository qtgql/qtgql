#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/ChangeUserBirth.hpp"
#include "graphql/__generated__/MainQuery.hpp"

namespace DateTimeTestCase {
using namespace qtgql;
auto ENV_NAME = QString("DateTimeTestCase");
auto SCHEMA_ADDR = get_server_address("2685696");

TEST_CASE("DateTimeTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    auto d = mq->get_data();
    auto now = QDateTime::currentDateTime(QTimeZone::utc())
                   .toString("hh:mm (dd.mm.yyyy)");
    REQUIRE(d->get_birth() == now);
  }
  SECTION("test update and as operation variables") {
    auto user = mq->get_data();
    auto modified_user_op = changeuserbirth::ChangeUserBirth::shared();
    auto new_birth = qtgql::customscalars::DateTimeScalar(
        QDateTime::currentDateTime().addDays(12));
    auto user_id = user->get_id();
    modified_user_op->set_variables({new_birth}, user_id);
    auto catcher =
        test_utils::SignalCatcher({.source_obj = user, .only = "birth"});
    modified_user_op->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(modified_user_op);
    REQUIRE(user->get_id() == modified_user_op->get_data()->get_id());
    REQUIRE(modified_user_op->get_data()->get_birth() == new_birth.to_qt());
    REQUIRE(user->get_birth() == new_birth.to_qt());
  };
}

}; // namespace DateTimeTestCase
