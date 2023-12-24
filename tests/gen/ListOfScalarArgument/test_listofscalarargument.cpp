#include "gen/EchoArg.hpp"
#include "testframework.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
namespace ListOfScalarArgument {
using namespace qtgql;

auto ENV_NAME = std::string("ListOfScalarArgument");
auto SCHEMA_ADDR =
    test_utils::get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("ListOfScalarArgument") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME,
      test_utils::DebugWsClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

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

}; // namespace ListOfScalarArgument
