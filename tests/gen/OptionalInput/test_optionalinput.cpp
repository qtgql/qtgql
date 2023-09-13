#include "gen/HelloOrEchoQuery.hpp"
#include "testframework.hpp"
#include "testutils.hpp"
#include <QSignalSpy>

namespace OptionalInput {
using namespace qtgql;

auto ENV_NAME = std::string("OptionalInput");
auto SCHEMA_ADDR = get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("OptionalInput") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto q = helloorechoquery::HelloOrEchoQuery::shared();
  SECTION("test deserialize") {
    QString to_compare = "foobar";
    q->set_variables({{to_compare}});
    q->fetch();
    test_utils::wait_for_completion(q);
    REQUIRE(q->data()->get_echoOrHello().toStdString().starts_with(
        to_compare.toStdString()));
  };
  SECTION("test update with variable") {
    QString to_compare = "foobar";
    q->set_variables({{to_compare}});
    q->fetch();
    test_utils::wait_for_completion(q);
    test_utils::SignalCatcher catcher(
        {.source_obj = q->data(), .only = "echoOrHello"});
    auto prev = q->data()->get_echoOrHello();
    q->refetch();
    REQUIRE(catcher.wait());
    REQUIRE(prev.toStdString() != q->data()->get_echoOrHello().toStdString());
  }
  SECTION("test deserialize no variable set.") {
    q->fetch();
    test_utils::wait_for_completion(q);
    REQUIRE(
        q->data()->get_echoOrHello().toStdString().starts_with("Hello World!"));
  };
  SECTION("test update no variable") {
    q->fetch();
    test_utils::wait_for_completion(q);
    test_utils::SignalCatcher catcher(
        {.source_obj = q->data(), .only = "echoOrHello"});
    auto prev = q->data()->get_echoOrHello();
    q->refetch();
    REQUIRE(catcher.wait());
    REQUIRE(prev.toStdString() != q->data()->get_echoOrHello().toStdString());
  }
}

}; // namespace OptionalInput
