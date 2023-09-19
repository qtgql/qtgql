#include "testframework.hpp"
#include <QSignalSpy>

#include "gen/MainQuery.hpp"
#include "gen/UpdateUserStatus.hpp"
#include "testutils.hpp"

namespace Enum {
using namespace qtgql;

auto ENV_NAME = std::string("Enum");
auto SCHEMA_ADDR = get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("Enum") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    REQUIRE_EQ(mq->data()->get_user()->get_status() , Enum::Enums::Connected);
  }
  SECTION("test updates and as operation variable") {
    auto update_status = updateuserstatus::UpdateUserStatus::shared();
    auto user = mq->data()->get_user();
    auto new_status = Enum::Enums::Disconnected;
    REQUIRE_NE(new_status , user->get_status());
    update_status->set_variables({user->get_id(), new_status});
    auto catcher =
        test_utils::SignalCatcher({.source_obj = user, .only = "status"});
    update_status->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(update_status);
    REQUIRE_EQ(user->get_status() , new_status);
  }
}

}; // namespace Enum
