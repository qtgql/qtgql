#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include "graphql/__generated__/UpdateUserName.hpp"

namespace NestedObjectTestCase {
using namespace qtgql;
auto ENV_NAME = QString("NestedObjectTestCase");
auto SCHEMA_ADDR = get_server_address("34284866");

TEST_CASE("NestedObjectTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{ .prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    auto name = mq->get_data()->get_person()->get_name();
    REQUIRE((!name.isEmpty() && name != bases::DEFAULTS::STRING));
  }
  SECTION("test updates"){
      auto user = mq->get_data();
      auto change_user_name_op  = updateusername::UpdateUserName::shared();
      QString new_name = "שלום";
      change_user_name_op->set_variables(user->get_id(), new_name);
      change_user_name_op->fetch();
      auto inner_person = user->get_person();
      auto catcher = test_utils::SignalCatcher(
              {.source_obj = inner_person, .only = "name"});
        REQUIRE(catcher.wait());

        test_utils::wait_for_completion(change_user_name_op);
      auto new_person = change_user_name_op->get_data()->get_person();
        REQUIRE(user->get_person()->get_id() == new_person->get_id());
        REQUIRE(user->get_person()->get_name() == new_name);
    }
        SECTION("test garbage collection") {
            auto node_id = mq->get_data()->get_person()->get_id();
            auto person = NestedObjectTestCase::Person::INST_STORE().get_node(node_id).value();
            // the map uses count and this reference, if the reference count decreased it means
            // that the instance store released its reference.
            REQUIRE(person.use_count() == 4);  // 1. map 2. at concrete user 3. at the proxy 4. here.
            mq->loose();
            REQUIRE(person.use_count() == 3);
        }
}

}; // namespace NestedObjectTestCase
