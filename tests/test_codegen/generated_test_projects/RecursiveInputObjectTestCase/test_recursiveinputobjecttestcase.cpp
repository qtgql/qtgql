#include "graphql/__generated__/MainQuery.hpp"
#include "test_codegen/generated_test_projects/RecursiveInputObjectTestCase/graphql/__generated__/schema.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>
#include <memory>

namespace RecursiveInputObjectTestCase {
using namespace qtgql;

auto ENV_NAME = std::string("RecursiveInputObjectTestCase");
auto SCHEMA_ADDR = get_server_address("RecursiveInputObjectTestCase");

TEST_CASE("RecursiveInputObjectTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") {
    auto mq = mainquery::MainQuery::shared();
    mq->set_variables(
        {RecursiveInput::create(RecursiveInput::create(std::nullopt, 2), 2)});
    mq->fetch();
    test_utils::wait_for_completion(mq);
    REQUIRE(mq->data()->get_depth() == 2);
  };
}
}; // namespace RecursiveInputObjectTestCase
