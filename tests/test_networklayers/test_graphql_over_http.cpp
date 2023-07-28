#include "debughandler.hpp"
#include "qtgql/gqloverhttp/gqloverhttp.hpp"
#include <catch2/catch_test_macros.hpp>
using namespace qtgql;

TEST_CASE("test_fetch", "[graphql-over-http]") {
  auto client =
      std::unique_ptr<gqloverhttp::NetworkLayer>{new gqloverhttp::NetworkLayer(
          test_utils::get_http_server_addr("graphql"), {})};
  SECTION("test simple query") {
    auto handler = std::make_shared<DebugHandler>("query HelloWorld{hello}");
    client->execute(handler);
    handler->wait_for_completed();
    REQUIRE(handler->m_data.value("hello").toString().toStdString() == "world");
  }
}
