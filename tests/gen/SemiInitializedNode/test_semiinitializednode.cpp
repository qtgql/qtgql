#include "gen/GetUserById.hpp"
#include "gen/PTLCreateUser.hpp"
#include "testframework.hpp"
#include "testutils.hpp"

namespace SemiInitializedNode {
    using namespace qtgql;

    auto ENV_NAME = std::string("SemiInitializedNode");
    auto SCHEMA_ADDR = test_utils::get_server_address(QString::fromStdString(ENV_NAME));

    TEST_CASE("SemiInitializedNode") {
        // resolves https://github.com/qtgql/qtgql/issues/381
        auto env = test_utils::get_or_create_env(
                ENV_NAME, test_utils::DebugClientSettings{.print_debug = true,
                        .prod_settings = {.url = SCHEMA_ADDR}});

        SECTION("test update on node type (cached) on possibly null fields.") {
            auto mq_partial = ptlcreateuser::PTLCreateUser::shared();
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

}; // namespace SemiInitializedNode
