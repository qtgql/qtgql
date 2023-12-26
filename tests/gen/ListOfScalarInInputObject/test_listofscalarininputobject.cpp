#include "gen/EchoArg.hpp"
#include "testframework.hpp"
#include "testutils.hpp"
#include <QSignalSpy>

namespace ListOfScalarInInputObject {
using namespace qtgql;

auto ENV_NAME = std::string("ListOfScalarInInputObject");
auto SCHEMA_ADDR =
    test_utils::get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("ListOfScalarInInputObject") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME,
      test_utils::DebugWsClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") {
    auto echo_op = echoarg::EchoArg::shared();
    std::list<QString> echo_me = {"A", "B", "C"};

    echo_op->set_variables({What::create(echo_me)});
    echo_op->execute();
    test_utils::wait_for_completion(echo_op);
    auto model = echo_op->data()->get_echo();
    REQUIRE(model->rowCount() > 0);
    int i = 0;
    for (const auto &expected : echo_me) {
      REQUIRE(model->get(i) == expected);
      i++;
    }
  };
}

}; // namespace ListOfScalarInInputObject
