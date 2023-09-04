#include "graphql/__generated__/EchoArg.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>
namespace ListOfScalarArgumentTestCase {
using namespace qtgql;

auto ENV_NAME = std::string("ListOfScalarArgumentTestCase");
auto SCHEMA_ADDR = get_server_address("ListOfScalarArgumentTestCase");

TEST_CASE("ListOfScalarArgumentTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") {
    auto mq = echoarg::EchoArg::shared();
    std::list<QString> echo_me = {"A", "B", "C"};
    mq->set_variables({.what = {echo_me}});
    mq->fetch();
    test_utils::wait_for_completion(mq);
    auto model = mq->data()->get_echo();
    REQUIRE(model->rowCount() > 0);
    int i = 0;
    for (const auto &expected : echo_me) {
      REQUIRE(model->get(i) == expected);
      i++;
    }
  };
}

}; // namespace ListOfScalarArgumentTestCase
