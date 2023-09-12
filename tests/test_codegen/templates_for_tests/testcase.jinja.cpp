#include <QSignalSpy>
#include "testframework.hpp"
#include "testutils.hpp"

namespace 👉 context.config.env_name 👈{
using namespace qtgql;

auto ENV_NAME = std::string("👉 context.config.env_name 👈");
auto SCHEMA_ADDR = get_server_address("👉 context.url_suffix 👈");

TEST_CASE("👉 context.test_name 👈", "[generated-testcase]") {
    auto env = test_utils::get_or_create_env(
            ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

    SECTION("test deserialize"){
        REQUIRE(false);
    };
    SECTION("test update"){
        REQUIRE(false);
    };

}

};