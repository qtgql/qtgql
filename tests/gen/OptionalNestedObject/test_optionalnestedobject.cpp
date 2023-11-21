#include "testframework.hpp"
#include <QSignalSpy>

#include "gen/MainQuery.hpp"
#include "gen/UpdateUserName.hpp"
#include "testutils.hpp"

namespace OptionalNestedObject {
using namespace qtgql;
auto ENV_NAME = std::string("OptionalNestedObject");
auto SCHEMA_ADDR =
    test_utils::get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("OptionalNestedObject") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME,
      test_utils::DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  SECTION("test deserialize") {
    SECTION("returned null") {
      mq->set_variables({true});
      qDebug() << "Fetching null person";
      mq->fetch();
      test_utils::wait_for_completion(mq);
      auto p = mq->data()->get_user()->get_person();
      REQUIRE(p == nullptr);
    };
    mq->set_variables({false});
    SECTION("returned value") {
      mq->fetch();
      test_utils::wait_for_completion(mq);
      auto p = mq->data()->get_user()->get_person();
      REQUIRE(p->get_name() == "nir");
    };
  }
  mq->set_variables({false});
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test updates") {
    auto old_user = mq->data()->get_user();
    auto change_user_name_op = updateusername::UpdateUserName::shared();
    QString new_name = "שלום";
    change_user_name_op->set_variables({old_user->get_id(), new_name});
    change_user_name_op->fetch();
    auto inner_person = old_user->get_person();
    auto catcher =
        test_utils::SignalCatcher({.source_obj = inner_person, .only = "name"});
    REQUIRE(catcher.wait());

    test_utils::wait_for_completion(change_user_name_op);
    auto new_person =
        change_user_name_op->data()->get_changeName()->get_person();
    REQUIRE(old_user->get_person()->get_id() == new_person->get_id());
    REQUIRE(old_user->get_person()->get_name() == new_name);
  }
}

}; // namespace OptionalNestedObject
