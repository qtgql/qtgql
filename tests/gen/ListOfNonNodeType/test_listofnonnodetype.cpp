#include "gen/ChangeUserName.hpp"
#include "gen/InsertUser.hpp"
#include "gen/MainQuery.hpp"
#include "testframework.hpp"
#include "testutils.hpp"
#include <QSignalSpy>

namespace ListOfNonNodeType {
using namespace qtgql;

auto ENV_NAME = std::string("ListOfNonNodeType");
auto SCHEMA_ADDR =
    test_utils::get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("ListOfNonNodeType") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME,
      test_utils::DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
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
    QString new_name(QUuid::createUuid().toString());
    REQUIRE(prev_name != new_name);
    auto change_username_mut = changeusername::ChangeUserName::shared();
    change_username_mut->set_variables({0, new_name});
    change_username_mut->fetch();
    test_utils::wait_for_completion(change_username_mut);
    test_utils::SignalCatcher catcher({.source_obj = user, .only = "name"});
    mq->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(mq);
    REQUIRE(user->get_name().toStdString() == new_name.toStdString());
  };
  SECTION("test update - insert new object at index") {
    auto model = mq->data()->get_users();
    auto prev_len = model->rowCount();
    auto insert_user = insertuser::InsertUser::shared();
    QString user_name("fobar");
    insert_user->set_variables({3, user_name});
    insert_user->fetch();
    test_utils::wait_for_completion(insert_user);
    mq->fetch();
    test_utils::wait_for_completion(mq);
    REQUIRE(model->rowCount() == prev_len + 1);
    REQUIRE(model->get(3)->get_name().toStdString() == user_name.toStdString());
  }
}

}; // namespace ListOfNonNodeType
