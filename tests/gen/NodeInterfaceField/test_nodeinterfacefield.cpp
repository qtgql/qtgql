#include "gen/ChangeName.hpp"
#include "gen/MainQuery.hpp"
#include "testframework.hpp"
#include "testutils.hpp"
#include <QSignalSpy>

namespace NodeInterfaceField {
using namespace qtgql;

auto ENV_NAME = std::string("NodeInterfaceField");
auto SCHEMA_ADDR =
    test_utils::get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("NodeInterfaceField") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME,
      test_utils::DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = mainquery::MainQuery::shared();
  mq->set_variables({NodeInterfaceField::Enums::TypesEnum::User});
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    REQUIRE(mq->data()->get_node()->property("__typeName") == "User");
    auto user =
        qobject_cast<const mainquery::User__node *>(mq->data()->get_node());
    REQUIRE(!user->get_password().isEmpty());
  };
  SECTION("test updates same id other operation") {
    auto user =
        qobject_cast<const mainquery::User__node *>(mq->data()->get_node());
    auto change_name_mut = changename::ChangeName::shared();
    QString new_name("Alfonso");
    change_name_mut->set_variables({user->get_id(), new_name});
    test_utils::SignalCatcher catcher({.source_obj = user, .only = "name"});
    change_name_mut->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(change_name_mut);

    REQUIRE(user->get_name().toStdString() == new_name.toStdString());
  };

  SECTION("test updates different id same type") {
    auto mq2 = mainquery::MainQuery::shared();
    test_utils::SignalCatcher catcher(
        {.source_obj = mq->data(), .only = "node"});
    mq2->set_variables({NodeInterfaceField::Enums::TypesEnum::User});
    mq2->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(mq2);
    auto user1 =
        qobject_cast<const mainquery::User__node *>(mq->data()->get_node());
    auto user2 =
        qobject_cast<const mainquery::User__node *>(mq2->data()->get_node());
    REQUIRE(user1->get_password() == user2->get_password());
  };
}
}; // namespace NodeInterfaceField
