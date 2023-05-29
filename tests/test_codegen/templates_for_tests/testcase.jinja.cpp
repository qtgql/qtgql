#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>
#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"

namespace 👉 context.config.env_name 👈{
using namespace qtgql;


TEST_CASE("👉 context.test_name 👈", "[generated-testcase]") {
    auto addr = get_server_address("👉 context.url_suffix 👈");
    auto client = new DebugAbleClient(DebugClientSettings{.prod_settings = {.url = addr}});
    client->wait_for_valid();

    bases::Environment::set_gql_env(std::make_shared<bases::Environment>(
            "👉 context.config.env_name 👈", std::unique_ptr<qtgql::gqlwstransport::GqlWsTransportClient>(client)
    ));

    REQUIRE(false);

}

};