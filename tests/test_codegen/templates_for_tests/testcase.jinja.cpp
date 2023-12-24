#include "testframework.hpp"
#include "testutils.hpp"

namespace 👉 context.config.env_name 👈{
using namespace qtgql;

auto ENV_NAME = std::string("👉 context.config.env_name 👈");

TEST_CASE("👉 context.test_name 👈") {
    auto SCHEMA_ADDR = test_utils::get_server_address(QString::fromStdString(ENV_NAME));
    test_utils::get_or_create_env(
            ENV_NAME, test_utils::DebugWsClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

    SECTION("test deserialize"){
        REQUIRE(false);
    };
    SECTION("test update"){
        REQUIRE(false);
    };

}

};