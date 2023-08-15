#include "graphql/__generated__/MainQuery.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace RootScalarTestCase {
using namespace qtgql;

auto ENV_NAME = QString("RootScalarTestCase");
auto SCHEMA_ADDR = get_server_address("RootScalarTestCase");

TEST_CASE("RootScalarTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = mainquery::MainQuery::shared();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") { REQUIRE(!mq->data()->get_name().isEmpty()); };
  SECTION("test update") {
    auto prev_name = mq->data()->get_name();
    auto catcher =
        test_utils::SignalCatcher({.source_obj = mq->data(), .only = "name"});
    auto mq2 = mainquery::MainQuery::shared();
    mq2->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(mq2);
    auto new_name = mq2->data()->get_name();
    REQUIRE(new_name != prev_name);
    REQUIRE(mq->data()->get_name() == new_name);
  };
}

}; // namespace RootScalarTestCase
