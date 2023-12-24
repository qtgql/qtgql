#include "testframework.hpp"
#include <QSignalSpy>
#include <QTest>

#include "gen/MainQuery.hpp"
#include "gen/UpdateBalance.hpp"
#include "testutils.hpp"

namespace Decimal {
using namespace qtgql;
auto ENV_NAME = std::string("Decimal");
auto SCHEMA_ADDR =
    test_utils::get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("Decimal") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME,
      test_utils::DebugWsClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
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

}; // namespace Decimal
