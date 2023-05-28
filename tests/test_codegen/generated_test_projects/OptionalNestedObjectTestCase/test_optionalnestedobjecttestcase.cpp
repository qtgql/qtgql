#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"

namespace OptionalNestedObjectTestCase {
using namespace qtgql;

TEST_CASE("OptionalNestedObjectTestCase", "[generated-testcase]") {
  auto addr = get_server_address("28655852");
  auto client =
      new DebugAbleClient(DebugClientSettings{.prod_settings = {.url = addr}});
  client->wait_for_valid();

  bases::Environment::set_gql_env(std::make_shared<bases::Environment>(
      "OptionalNestedObjectTestCase",
      std::unique_ptr<qtgql::gqlwstransport::GqlWsTransportClient>(client)));

  auto mq = std::make_shared<mainquery::MainQuery>();
  SECTION("returned null") {
    mq->setVariables({true});
    mq->fetch();
    test_utils::wait_for_completion(mq);
    auto p = mq->get_data()->get_person();
    qDebug() << p;
    qDebug() << &p;
    REQUIRE(p == nullptr);
  };
  SECTION("returned value") {
    mq->setVariables({false});
    mq->fetch();
    test_utils::wait_for_completion(mq);
    auto p = mq->get_data()->get_person();
    REQUIRE(p->get_name() == "nir");
  };
}

};  // namespace OptionalNestedObjectTestCase
