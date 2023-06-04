#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/CreatePost.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include "graphql/__generated__/changePostHeaderMutation.hpp"

namespace OperationVariableTestCase {
using namespace qtgql;

auto ENV_NAME = QString("OperationVariableTestCase");
auto SCHEMA_ADDR = get_server_address("5881041");

TEST_CASE("OperationVariableTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize"){SECTION("scalars"){
      auto main_query = std::make_shared<mainquery::MainQuery>();
  main_query->fetch();
  test_utils::wait_for_completion(main_query);
  auto post_id = main_query->get_data()->get_id();
  auto prev_header = main_query->get_data()->get_header();
  auto change_post_mutation =
      std::make_shared<changepostheadermutation::changePostHeaderMutation>();
  change_post_mutation->set_variables(post_id, "Cool Header");
  change_post_mutation->fetch();
  test_utils::wait_for_completion(change_post_mutation);
  qDebug() << main_query->get_data()->get_header();
  REQUIRE(main_query->get_data()->get_header() == "Cool Header");
}

};  // namespace OperationVariableTestCase
}
}
;  // namespace OperationVariableTestCase
