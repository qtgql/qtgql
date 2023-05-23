#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>
#include "debugableclient.hpp"
namespace 👉 context.config.env_name 👈{


TEST_CASE("👉 context.test_name 👈", "[generated-testcase]") {
    auto addr = get_server_address("👉 context.url_suffix 👈");
    auto client = new DebugAbleClient(DebugClientSettings{.prod_settings = {.url = addr}});
    client->wait_for_valid();

    qtgql::Environment::set_gql_env(std::make_shared<qtgql::Environment>(
            "👉 context.config.env_name 👈", std::unique_ptr<qtgql::GqlWsTransportClient>(client)
    ));

    REQUIRE(false);

}

};