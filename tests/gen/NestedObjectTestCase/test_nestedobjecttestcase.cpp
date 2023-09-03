#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "g/MainQuery.hpp"
#include "g/ReplacePerson.hpp"
#include "g/UpdateUserName.hpp"
#include "testutils.hpp"

namespace NestedObjectTestCase {
using namespace qtgql;
auto ENV_NAME = QString("NestedObjectTestCase");
auto SCHEMA_ADDR = get_server_address("NestedObjectTestCase");

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
    auto user_inst_from_mq = mq->data()->get_user();
    auto old_user_id = user_inst_from_mq->get_id();
    auto old_person_name = user_inst_from_mq->get_person()->get_name();
    auto old_person_id = user_inst_from_mq->get_person()->get_id();
    auto replace_person_op = replaceperson::ReplacePerson::shared();
    replace_person_op->set_variables({old_user_id});
    replace_person_op->fetch();
    // The current mechanism is to replace the instance with the new concrete.
    auto catcher = test_utils::SignalCatcher(
        {.source_obj = user_inst_from_mq->get_person(), .only = "name"});
    REQUIRE(catcher.wait());

    test_utils::wait_for_completion(replace_person_op);
    auto new_person =
        replace_person_op->data()->get_replacePerson()->get_person();

    REQUIRE(new_person->get_id() != old_person_id);
    REQUIRE(new_person->get_id() == user_inst_from_mq->get_person()->get_id());
    REQUIRE(new_person->get_name().toStdString() !=
            old_person_name.toStdString());
    REQUIRE(new_person->get_name() ==
            user_inst_from_mq->get_person()->get_name());
  }
}

}; // namespace NestedObjectTestCase
