#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "graphql/__generated__/ChangeUserBirth.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include "testutils.hpp"

namespace DateTestCase {
using namespace qtgql;
auto ENV_NAME = QString("DateTestCase");
auto SCHEMA_ADDR = get_server_address("DateTestCase");

TEST_CASE("DateTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.print_debug = false,
                                    .prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    auto user = mq->data()->get_user();
    auto now = QDate::currentDate().toString("dd.MM.yyyy");
    REQUIRE(user->get_birth() == now);
  }
  SECTION("test update and as operation variables") {
    auto old_user = mq->data()->get_user();
    auto modified_user_op = changeuserbirth::ChangeUserBirth::shared();
    auto new_birth =
        customscalars::DateScalar(QDate::currentDate().addDays(12));
    auto user_id = old_user->get_id();
    modified_user_op->set_variables({{new_birth}, user_id});
    auto catcher =
        test_utils::SignalCatcher({.source_obj = old_user, .only = "birth"});
    modified_user_op->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(modified_user_op);
    auto new_user = modified_user_op->data()->get_changeBirth();
    REQUIRE(old_user->get_id() == new_user->get_id());
    REQUIRE(new_user->get_birth() == new_birth.to_qt());
    REQUIRE(old_user->get_birth() == new_birth.to_qt());
  };
}

}; // namespace DateTestCase
