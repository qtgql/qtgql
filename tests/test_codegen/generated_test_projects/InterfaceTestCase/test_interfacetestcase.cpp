#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/AnimalQuery.hpp"

namespace InterfaceTestCase {
using namespace qtgql;

auto ENV_NAME = QString("InterfaceTestCase");
auto SCHEMA_ADDR = get_server_address("31367495");

TEST_CASE("InterfaceTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto animal_query = animalquery::AnimalQuery::shared();
  animal_query->set_variables({InterfaceTestCase::Enums::AnimalKind::DOG});
  animal_query->fetch();
  test_utils::wait_for_completion(animal_query);
  SECTION("test deserialize") {
    auto animal = animal_query->data()->get_animal();
    REQUIRE(animal->get_kind() == InterfaceTestCase::Enums::AnimalKind::DOG);
  };
}

}; // namespace InterfaceTestCase
