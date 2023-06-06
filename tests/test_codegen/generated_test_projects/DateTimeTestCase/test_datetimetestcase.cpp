#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
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
  //          SECTION("test update") {
  //              auto user = mq->get_data();
  //              auto previous_name = mq->get_data()->get_name();
  //              auto modified_user_op =
  //              userwithsameidanddifferentfieldsquery::
  //              UserWithSameIDAndDifferentFieldsQuery::shared();
  //              auto catcher = test_utils::SignalCatcher(user);
  //              modified_user_op->fetch();
  //              REQUIRE(catcher.wait());
  //              test_utils::wait_for_completion(modified_user_op);
  //              REQUIRE(user->get_id() ==
  //              modified_user_op->get_data()->get_id()); auto new_name =
  //              modified_user_op->get_data()->get_name();
  //              REQUIRE(user->get_name() == new_name);
  //              REQUIRE(new_name != previous_name);
  //          };
}

};  // namespace DateTimeTestCase
