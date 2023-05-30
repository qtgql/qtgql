#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>
#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"

namespace 👉 context.config.env_name 👈{
using namespace qtgql;

auto ENV_NAME = QString("👉 context.config.env_name 👈");
auto SCHEMA_ADDR = get_server_address("👉 context.url_suffix 👈");

TEST_CASE("👉 context.test_name 👈", "[generated-testcase]") {
    auto env = test_utils::get_or_create_env(
            ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

    REQUIRE(false);

}

};