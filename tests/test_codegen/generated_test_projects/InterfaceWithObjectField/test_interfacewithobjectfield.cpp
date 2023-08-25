#include "graphql/__generated__/AnimalQuery.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace InterfaceWithObjectField {
using namespace qtgql;

auto ENV_NAME = QString("InterfaceWithObjectField");
auto SCHEMA_ADDR = get_server_address("InterfaceWithObjectField");

TEST_CASE("InterfaceWithObjectField", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") {
    auto animal_query = animalquery::AnimalQuery::shared();
    animal_query->set_variables({Enums::AnimalKind::DOG});
    animal_query->fetch();
    test_utils::wait_for_completion(animal_query);
    auto animal = animal_query->data()->get_animal();
    REQUIRE(animal->get_metadata()->get_kind() == Enums::AnimalKind::DOG);
    auto dog = qobject_cast<const animalquery::Dog__animal *>(animal);
    REQUIRE(!dog->get_furColor().isEmpty());
  };
}

}; // namespace InterfaceWithObjectField
