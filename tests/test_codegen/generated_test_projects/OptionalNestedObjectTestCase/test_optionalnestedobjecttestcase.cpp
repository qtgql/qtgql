#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "graphql/__generated__/MainQuery.hpp"
#include "graphql/__generated__/UpdateUserName.hpp"
#include "testutils.hpp"

namespace OptionalNestedObjectTestCase {
using namespace qtgql;
auto ENV_NAME = QString("OptionalNestedObjectTestCase");
auto SCHEMA_ADDR = get_server_address("45810550");

TEST_CASE("OptionalNestedObjectTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
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

}; // namespace OptionalNestedObjectTestCase
