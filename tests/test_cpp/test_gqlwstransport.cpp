#include <catch2/catch_test_macros.hpp>
#include <gqltransport.hpp>

static int return_two(int number) { return 2; };
QString get_server_addr() {
  if (const char* addr = std::getenv("SCHEMAS_SERVER_ADDR")) {
    return QString(addr);
  }
  throw "No server address found";
}

TEST_CASE("get operation name", "[single-file]") {
  const QString operation_name = " SampleOperation";
  auto res_op_name =
      get_operation_name("query SampleOperation {field1 field2}");
  REQUIRE(res_op_name.value() == operation_name);
};

TEST_CASE("grahpql-ws-transport protocol", "[single-file]") {
  auto addr = get_server_addr();
  auto client = GqlWsTransportClient(addr);
}
