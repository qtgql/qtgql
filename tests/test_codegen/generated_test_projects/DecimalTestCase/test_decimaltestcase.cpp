#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include "graphql/__generated__/UpdateBalance.hpp"

namespace DecimalTestCase {
using namespace qtgql;
auto ENV_NAME = QString("DecimalTestCase");
auto SCHEMA_ADDR = get_server_address("33070556");

TEST_CASE("DecimalTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);

  SECTION("test deserialize") {
    REQUIRE(!mq->get_data()->get_balance().isEmpty());
  }
  SECTION("test update and as operation variables") {
    auto user = mq->get_data();
    auto modified_user_op = updatebalance::UpdateBalance::shared();
    auto new_balance = customscalars::DecimalScalar(
        mq->get_data()->get_balance() + "122121554545");
    auto user_id = user->get_id();
    modified_user_op->set_variables({new_balance}, user_id);
    auto catcher =
        test_utils::SignalCatcher({.source_obj = user, .only = "birth"});
    modified_user_op->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(modified_user_op);
    REQUIRE(user->get_id() == modified_user_op->get_data()->get_id());
    REQUIRE(modified_user_op->get_data()->get_balance() == new_balance.to_qt());
    REQUIRE(user->get_balance() == new_balance.to_qt());
  };
}

};  // namespace DecimalTestCase
