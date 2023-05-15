#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>
#include "debugableclient.hpp"



TEST_CASE("👉 context.test_name 👈") {
    auto client = new DebugAbleClient({.prod_settings = {.url = {"👉 context.url 👈"}}});
    client->wait_for_valid();
    qtgql::QtGqlEnvironment::set_gql_env(std::make_shared<qtgql::QtGqlEnvironment>(
            "👉 context.config.env_name 👈", std::unique_ptr<qtgql::GqlWsTransportClient>(client)
            ));

	REQUIRE(false);

    delete client;
}