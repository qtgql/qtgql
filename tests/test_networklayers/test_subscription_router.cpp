#include "qtgql/gqloverhttp/gqloverhttp.hpp"
#include "qtgql/routers/detail/routers.hpp"
#include "utils.hpp"
#include <catch2/catch_test_macros.hpp>
using namespace qtgql;

TEST_CASE("test subscription router", "[subscription router]") {
  auto http_layer = std::shared_ptr<gqloverhttp::GraphQLOverHttp>{
      new gqloverhttp::GraphQLOverHttp(
          test_utils::get_http_server_addr("graphql"), {})};
  auto ws_layer = get_valid_ws_client();
  auto client =
      std::make_shared<routers::SubscriptionRouter>(ws_layer, http_layer);
  SECTION("test simple query") {
    auto handler = std::make_shared<DebugHandler>("query HelloWorld{hello}");
    client->execute(handler);
    handler->wait_for_completed();
    REQUIRE(handler->m_data.value("hello").toString().toStdString() == "world");
  }

  SECTION("test error") {
    auto handler =
        std::make_shared<DebugHandler>("query HelloWorld{raiseError}");
    client->execute(handler);
    handler->wait_for_completed();
    qDebug() << handler->m_errors;
    REQUIRE(handler->m_errors.first()
                .toObject()
                .value("message")
                .toString()
                .toStdString() == "foobar");
  }

  SECTION("test subscription") {
    auto handler = std::make_shared<DebugHandler>(get_subscription_str());
    client->execute(handler);
    REQUIRE(
        QTest::qWaitFor([&]() -> bool { return handler->count_eq_9(); }, 1500));
  }
}
