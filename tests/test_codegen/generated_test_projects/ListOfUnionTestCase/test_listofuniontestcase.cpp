#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace ListOfUnionTestCase {
using namespace qtgql;

auto ENV_NAME = QString("ListOfUnionTestCase");
auto SCHEMA_ADDR = get_server_address("70862812");

TEST_CASE("ListOfUnionTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = mainquery::MainQuery::shared();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    auto root = mq->data();
    auto model = root->get_usersAndFrogs();
    auto union_data = model->first();
    auto type_name = union_data->__typename();
    if (type_name == "Frog") {
      REQUIRE(!qobject_cast<mainquery::Frog__usersAndFrogs *>(union_data)
                   ->get_color()
                   .isEmpty());
    } else {
      REQUIRE(qobject_cast<mainquery::Person__usersAndFrogs *>(union_data)
                  ->get_age() > 0);
    }
  };
  SECTION("test update") { REQUIRE(false); };
}

}; // namespace ListOfUnionTestCase
