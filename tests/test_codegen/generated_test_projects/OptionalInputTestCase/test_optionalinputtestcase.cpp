#include "graphql/__generated__/HelloOrEchoQuery.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace OptionalInputTestCase {
using namespace qtgql;

auto ENV_NAME = QString("OptionalInputTestCase");
auto SCHEMA_ADDR = get_server_address("OptionalInputTestCase");

TEST_CASE("OptionalInputTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") {
    auto q = helloorechoquery::HelloOrEchoQuery::shared();
    QString to_compare = "foobar";
    q->set_variables({{to_compare}});
    q->fetch();
    test_utils::wait_for_completion(q);
    REQUIRE(q->data()->get_echoOrHello().toStdString() ==
            to_compare.toStdString());
  };
  SECTION("test update") { REQUIRE(false); };
}

}; // namespace OptionalInputTestCase
