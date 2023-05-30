#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"

namespace OptionalNestedObjectTestCase {
using namespace qtgql;
auto ENV_NAME = QString("OptionalNestedObjectTestCase");
auto SCHEMA_ADDR = get_server_address("28655852");

TEST_CASE("OptionalNestedObjectTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
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
