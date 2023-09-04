#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "graphql/__generated__/MainQuery.hpp"
#include "graphql/__generated__/UpdateUserStatus.hpp"
#include "testutils.hpp"

namespace EnumTestCase {
using namespace qtgql;

auto ENV_NAME = std::string("EnumTestCase");
auto SCHEMA_ADDR = get_server_address("EnumTestCase");

TEST_CASE("EnumTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    REQUIRE(mq->data()->get_user()->get_status() ==
            EnumTestCase::Enums::Connected);
  }
  SECTION("test updates and as operation variable") {
    auto update_status = updateuserstatus::UpdateUserStatus::shared();
    auto user = mq->data()->get_user();
    auto new_status = EnumTestCase::Enums::Disconnected;
    REQUIRE(new_status != user->get_status());
    update_status->set_variables({user->get_id(), new_status});
    auto catcher =
        test_utils::SignalCatcher({.source_obj = user, .only = "status"});
    update_status->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(update_status);
    REQUIRE(user->get_status() == new_status);
  }
}

}; // namespace EnumTestCase
