#include "gen/CreateUser_Partial.hpp"
#include "gen/GetUserById.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include "testframework.hpp"

namespace PartiallyInitializedNodeUpdate {
using namespace qtgql;

auto ENV_NAME = std::string("PartiallyInitializedNodeUpdate");
auto SCHEMA_ADDR = get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("PartiallyInitializedNodeUpdate") {
  // resolves https://github.com/qtgql/qtgql/issues/381
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.print_debug = true,
                                    .prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test update on node type (cached) on possibly null fields.") {
    auto mq_partial = createuser_partial::CreateUser_Partial::shared();
    mq_partial->fetch();
    test_utils::wait_for_completion(mq_partial);
    REQUIRE(mq_partial->data()->get_createUser()->get_age() > 0);
    auto user_id = mq_partial->data()->get_createUser()->get_id();
    auto full_user = getuserbyid::GetUserById::shared();
    full_user->set_variables({user_id});
    full_user->fetch();
    test_utils::wait_for_completion(full_user);
  };
}

}; // namespace PartiallyInitializedNodeUpdate
