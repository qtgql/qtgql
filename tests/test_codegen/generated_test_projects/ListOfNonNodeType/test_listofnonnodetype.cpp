#include "debugableclient.hpp"
#include "graphql/__generated__/ChangeUserName.hpp"
#include "graphql/__generated__/InsertUser.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace ListOfNonNodeType {
using namespace qtgql;

auto ENV_NAME = QString("ListOfNonNodeType");
auto SCHEMA_ADDR = get_server_address("83923371");

TEST_CASE("ListOfNonNodeType", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = mainquery::MainQuery::shared();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    auto user = mq->data()->get_users()->first();
    REQUIRE(!user->get_name().isEmpty());
  };
  SECTION("test update - modify attributes at index") {
    auto user = mq->data()->get_users()->first();
    auto prev_name = user->get_name();
    QString new_name("Ma");
    REQUIRE(prev_name != new_name);
    auto change_username_mut = changeusername::ChangeUserName::shared();
    change_username_mut->set_variables({0, new_name});
    change_username_mut->fetch();
    test_utils::wait_for_completion(change_username_mut);
    test_utils::SignalCatcher catcher({.source_obj = user, .only = "name"});
    mq->refetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(mq);
    REQUIRE(user->get_name().toStdString() == new_name.toStdString());
  };
}

}; // namespace ListOfNonNodeType
