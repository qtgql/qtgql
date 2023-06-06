#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
namespace NestedObjectTestCase {
using namespace qtgql;
auto ENV_NAME = QString("NestedObjectTestCase");
auto SCHEMA_ADDR = get_server_address("26433428");

TEST_CASE("NestedObjectTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    auto name = mq->get_data()->get_person()->get_name();
    REQUIRE((!name.isEmpty() && name != bases::DEFAULTS::STRING));
  }
}

}; // namespace NestedObjectTestCase
