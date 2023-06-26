#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace NonNodeTypeTestCase {
using namespace qtgql;

auto ENV_NAME = QString("NonNodeTypeTestCase");
auto SCHEMA_ADDR = get_server_address("70127411");

TEST_CASE("NonNodeTypeTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = mainquery::MainQuery::shared();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    REQUIRE(!mq->data()->get_user()->get_name().isEmpty());
  };
  SECTION("test update") {
    auto prev_name = mq->data()->get_user()->get_name();
    auto mq2 = mainquery::MainQuery::shared();
    mq2->fetch();
    test_utils::wait_for_completion(mq2);
    auto new_name = mq2->data()->get_user()->get_name();
    qDebug() << new_name << "old name is " << prev_name;
    REQUIRE(prev_name != new_name);
    REQUIRE(new_name == mq->data()->get_user()->get_name());
  };
}

}; // namespace NonNodeTypeTestCase
