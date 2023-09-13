#include "gen/MainQuery.hpp"
#include "qtgql/gqloverhttp/gqloverhttp.hpp"
#include "testframework.hpp"
#include "testutils.hpp"
#include <QSignalSpy>

namespace GqlOverHttpAsEnv {
using namespace qtgql;

auto ENV_NAME = std::string("GqlOverHttpAsEnv");
auto SCHEMA_ADDR = test_utils::get_http_server_addr("GqlOverHttpAsEnv");

TEST_CASE("GqlOverHttpAsEnv") {

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

}; // namespace GqlOverHttpAsEnv
