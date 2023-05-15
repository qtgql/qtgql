#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>



TEST_CASE("👉 context.test_name 👈") {
    auto client = new qtgql::GqlWsTransportClient({.url = {"👉 context.url 👈"}});
    REQUIRE(QTest::qWaitFor([&]() -> bool { return client->is_valid(); }, 1500));

    qtgql::QtGqlEnvironment::set_gql_env(std::make_shared<qtgql::QtGqlEnvironment>(
            "👉 context.config.env_name 👈", std::unique_ptr<qtgql::GqlWsTransportClient>(client)
            ));

	REQUIRE(false);

    delete client;
}