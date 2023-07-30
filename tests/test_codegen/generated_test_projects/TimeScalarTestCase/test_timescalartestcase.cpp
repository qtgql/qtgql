#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "graphql/__generated__/MainQuery.hpp"
#include "graphql/__generated__/UpdateLunchTime.hpp"
#include "testutils.hpp"

namespace TimeScalarTestCase {
using namespace qtgql;
auto ENV_NAME = QString("TimeScalarTestCase");
auto SCHEMA_ADDR = get_server_address("TimeScalarTestCase");

TEST_CASE("TimeScalarTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    auto user = mq->data()->get_user();
    auto now = QDateTime::currentDateTime(QTimeZone::utc()).time().toString();
    REQUIRE(user->get_lunchTime() == now);
  }
  SECTION("test update and as operation variables") {
    auto old_user = mq->data()->get_user();
    auto modified_user_op = updatelunchtime::UpdateLunchTime::shared();
    auto new_lunch_time =
        customscalars::TimeScalar(QTime::currentTime().addSecs(20));
    auto user_id = old_user->get_id();
    modified_user_op->set_variables({{new_lunch_time}, user_id});
    auto catcher = test_utils::SignalCatcher(
        {.source_obj = old_user, .only = "lunchTime"});
    modified_user_op->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(modified_user_op);
    auto new_user = modified_user_op->data()->get_changeLunchTime();
    REQUIRE(old_user->get_id() == new_user->get_id());
    REQUIRE(new_user->get_lunchTime() == new_lunch_time.to_qt());
    REQUIRE(old_user->get_lunchTime() == new_lunch_time.to_qt());
  };
}

}; // namespace TimeScalarTestCase
