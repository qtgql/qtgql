#include "g/MainQuery.hpp"
#include "qtgql/gqloverhttp/gqloverhttp.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace GqlOverHttpAsEnvTestCase {
using namespace qtgql;

auto ENV_NAME = QString("GqlOverHttpAsEnvTestCase");
auto SCHEMA_ADDR = test_utils::get_http_server_addr("GqlOverHttpAsEnvTestCase");

TEST_CASE("GqlOverHttpAsEnvTestCase", "[generated-testcase]") {

  SECTION("test deserialize") {
    auto gql_over_http = std::unique_ptr<gqloverhttp::GraphQLOverHttp>{
        new gqloverhttp::GraphQLOverHttp(SCHEMA_ADDR, {})};
    auto env = std::make_shared<bases::Environment>(ENV_NAME,
                                                    std::move(gql_over_http));
    bases::Environment::set_gql_env(env);
    auto mq = std::make_shared<mainquery::MainQuery>();
    mq->fetch();
    test_utils::wait_for_completion(mq);
    auto d = mq->data()->get_constUser();
    REQUIRE(d->get_age() == 24);
    REQUIRE(d->get_agePoint() == 24.0f);
    REQUIRE(d->get_id() == "FakeID");
    REQUIRE(d->get_male() == true);
    REQUIRE(d->get_name() == "nir");
    REQUIRE(d->get_uuid() ==
            QUuid::fromString("06335e84-2872-4914-8c5d-3ed07d2a2f16"));
    REQUIRE(d->get_voidField() == qtgql::bases::DEFAULTS::VOID);
  };
}

}; // namespace GqlOverHttpAsEnvTestCase
