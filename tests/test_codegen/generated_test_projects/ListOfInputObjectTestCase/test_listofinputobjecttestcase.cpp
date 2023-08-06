#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>
#include "testutils.hpp"
#include "graphql/__generated__/MainQuery.hpp"

namespace ListOfInputObjectTestCase{
using namespace qtgql;

auto ENV_NAME = QString("ListOfInputObjectTestCase");
auto SCHEMA_ADDR = get_server_address("ListOfInputObjectTestCase");

TEST_CASE("ListOfInputObjectTestCase", "[generated-testcase]") {
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