#include "graphql/__generated__/MainQuery.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>
#include <list>

namespace ListOfInputObjectTestCase {
using namespace qtgql;

auto ENV_NAME = QString("ListOfInputObjectTestCase");
auto SCHEMA_ADDR = get_server_address("ListOfInputObjectTestCase");

TEST_CASE("ListOfInputObjectTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") {
    auto echo_query = mainquery::MainQuery::shared();
    std::list<ListOfInputObjectTestCase::Echo> what_list = {
        {"What"}, {"Am"}, {"I"}};
    echo_query->set_variables(
        {ListOfInputObjectTestCase::What::create(what_list)});
    echo_query->fetch();
    test_utils::wait_for_completion(echo_query);
    auto model = echo_query->data()->get_echo();
    REQUIRE(model->rowCount() > 0);
    int i = 0;
    for (const auto &expected : what_list) {
      REQUIRE(model->get(i) == expected.value);
      i++;
    }
  };
}
}; // namespace ListOfInputObjectTestCase
