#include <QTest>
#include <catch2/catch_test_macros.hpp>
#include <gqltransport.hpp>

#include "main.hpp"
static int return_two(int number) { return 2; };

TEST_CASE("get operation name", "[single-file]") {
  const QString operation_name = " SampleOperation";
  auto res_op_name =
      get_operation_name("query SampleOperation {field1 field2}");
  REQUIRE(res_op_name.value() == operation_name);
};

TEST_CASE("grahpql-ws-transport protocol", "[single-file]") {
  QString addr = "ws://localhost:8546/graphql";
  auto client = GqlWsTransportClient(addr);
  auto success = QTest::qWaitFor([&]() { return client.is_valid(); }, 100);
  REQUIRE(success);
}
