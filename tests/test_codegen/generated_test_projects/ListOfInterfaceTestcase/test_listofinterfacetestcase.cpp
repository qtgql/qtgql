#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace ListOfInterfaceTestcase {
using namespace qtgql;

auto ENV_NAME = QString("ListOfInterfaceTestcase");
auto SCHEMA_ADDR = get_server_address("25272377");

TEST_CASE("ListOfInterfaceTestcase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = mainquery::MainQuery::shared();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    auto root = mq->data();
    auto model = root->get_randPerson()->get_pets();
    auto pet_interface = model->first();
    auto type_name = pet_interface->__typename();
    if (type_name == "Cat") {
      REQUIRE(!qobject_cast<mainquery::Cat__randPersonpets *>(pet_interface)
                   ->get_color()
                   .isEmpty());
    } else {
      REQUIRE(qobject_cast<mainquery::Dog__randPersonpets *>(pet_interface)
                  ->get_age() > 0);
    }
  };
  SECTION("test update") { REQUIRE(false); };
}

}; // namespace ListOfInterfaceTestcase
