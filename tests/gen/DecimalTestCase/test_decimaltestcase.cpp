#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "g/MainQuery.hpp"
#include "g/UpdateBalance.hpp"
#include "testutils.hpp"

namespace DecimalTestCase {
using namespace qtgql;
auto ENV_NAME = QString("DecimalTestCase");
auto SCHEMA_ADDR = get_server_address("DecimalTestCase");

TEST_CASE("DecimalTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);

  SECTION("test deserialize") {
    REQUIRE(!mq->data()->get_user()->get_balance().isEmpty());
  }
  SECTION("test update and as operation variable") {
    auto old_user = mq->data()->get_user();
    auto modified_user_op = updatebalance::UpdateBalance::shared();
    auto new_balance =
        customscalars::DecimalScalar(old_user->get_balance() + "122121554545");
    auto user_id = old_user->get_id();
    modified_user_op->set_variables({{new_balance}, user_id});
    auto catcher =
        test_utils::SignalCatcher({.source_obj = old_user, .only = "balance"});
    modified_user_op->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(modified_user_op);
    auto new_user = modified_user_op->data()->get_changeBalance();
    REQUIRE(old_user->get_id() == new_user->get_id());
    REQUIRE(new_user->get_balance() == new_balance.to_qt());
    REQUIRE(old_user->get_balance() == new_balance.to_qt());
  };
}

}; // namespace DecimalTestCase
