#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "graphql/__generated__/MainQuery.hpp"
#include "graphql/__generated__/ReplacePerson.hpp"
#include "graphql/__generated__/UpdateUserName.hpp"
#include "testutils.hpp"

namespace NestedObjectTestCase {
using namespace qtgql;
auto ENV_NAME = QString("NestedObjectTestCase");
auto SCHEMA_ADDR = get_server_address("9416609");

TEST_CASE("NestedObjectTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    auto name = mq->data()->get_user()->get_person()->get_name();
    REQUIRE((!name.isEmpty() && name != bases::DEFAULTS::STRING));
  }
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
  SECTION("test update returned entirely new node") {
    auto old_user = mq->data()->get_user();
    auto replace_person_op = replaceperson::ReplacePerson::shared();
    replace_person_op->set_variables({old_user->get_id()});
    replace_person_op->fetch();
    auto catcher =
        test_utils::SignalCatcher({.source_obj = old_user, .only = "person"});
    REQUIRE(catcher.wait());

    test_utils::wait_for_completion(replace_person_op);
    auto new_person =
        replace_person_op->data()->get_replacePerson()->get_person();

    REQUIRE(old_user->get_person()->get_id() == new_person->get_id());
    REQUIRE(old_user->get_person()->get_name() == new_person->get_name());
  }
}

}; // namespace NestedObjectTestCase
