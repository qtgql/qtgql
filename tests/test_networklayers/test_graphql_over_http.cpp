#include "qtgql/gqloverhttp/gqloverhttp.hpp"
#include "testframework.hpp"
#include "utils.hpp"
using namespace qtgql;

TEST_CASE("test graphql over http") {
  auto client = std::unique_ptr<gqloverhttp::GraphQLOverHttp>{
      new gqloverhttp::GraphQLOverHttp(
          test_utils::get_http_server_addr("graphql"), {})};
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

  SECTION("test headers") {
    std::string expected_ret = "The resolver will return this";
    client->set_headers({{"Authorization", expected_ret}});
    auto handler =
        std::make_shared<DebugHandler>("query MyQuery {isAuthenticated}");
    client->execute(handler);
    handler->wait_for_completed();
    REQUIRE(handler->m_data["isAuthenticated"].toString().toStdString() ==
            expected_ret);
  }
  SECTION("test http error") {
    client->set_headers({{"raise_http_error", "true"}});
    auto handler =
        std::make_shared<DebugHandler>("query HelloWorld{raiseError}");
    client->execute(handler);
    handler->wait_for_completed();
    REQUIRE(handler->m_errors.first()
                .toObject()
                .value("message")
                .toString()
                .contains("This is a test error"));
  }
}
