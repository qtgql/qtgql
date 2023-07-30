#include "graphql/__generated__/ChangeFriendName.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace OperationVariablesTestcase {
using namespace qtgql;

auto ENV_NAME = QString("OperationVariablesTestcase");
auto SCHEMA_ADDR = get_server_address("OperationVariablesTestcase");

TEST_CASE("OperationVariablesTestcase", "[generated-testcase]") {

  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = mainquery::MainQuery::shared();
  mq->set_variables({true});
  mq->fetch();
  test_utils::wait_for_completion(mq);

  SECTION("test deserialize") {
    auto user = mq->data()->get_user();
    REQUIRE(!user->get_name().isEmpty());
    REQUIRE(!user->get_friend()->get_name().isEmpty());
  };
  SECTION("test update") {
    auto user = mq->data()->get_user();
    auto change_name_mut = changefriendname::ChangeFriendName::shared();
    change_name_mut->set_variables({true, "Yehoshua"});
    test_utils::SignalCatcher catcher(
        {.source_obj = user->get_friend(), .only = "name"});
    change_name_mut->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(change_name_mut);
    REQUIRE(user->get_friend()->get_name() == "Yehoshua");
  };
}

}; // namespace OperationVariablesTestcase
