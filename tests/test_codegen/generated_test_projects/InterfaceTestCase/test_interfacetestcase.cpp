#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/GetUser.hpp"
#include "graphql/__generated__/NodeForUser.hpp"

namespace InterfaceTestCase {
using namespace qtgql;

auto ENV_NAME = QString("InterfaceTestCase");
auto SCHEMA_ADDR = get_server_address("72035854");

TEST_CASE("InterfaceTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto user_query = getuser::GetUser::shared();
  user_query->fetch();
  test_utils::wait_for_completion(user_query);
  SECTION("test deserialize") {
    auto user = user_query->data()->get_user();
    auto node_query = nodeforuser::NodeForUser::shared();
    node_query->set_variables({user->get_id()});
    node_query->fetch();
    test_utils::wait_for_completion(node_query);
    REQUIRE(node_query->data()->get_node())
  };
}

}; // namespace InterfaceTestCase
