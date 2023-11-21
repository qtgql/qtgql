#include "gen/MainQuery.hpp"
#include "testframework.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <list>

namespace ListOfInputObject {
using namespace qtgql;

auto ENV_NAME = std::string("ListOfInputObject");
auto SCHEMA_ADDR =
    test_utils::get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("ListOfInputObject") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME,
      test_utils::DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") {
    auto echo_query = mainquery::MainQuery::shared();
    std::list<ListOfInputObject::Echo> what_list = {{"What"}, {"Am"}, {"I"}};
    echo_query->set_variables({ListOfInputObject::What::create(what_list)});
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
}; // namespace ListOfInputObject
