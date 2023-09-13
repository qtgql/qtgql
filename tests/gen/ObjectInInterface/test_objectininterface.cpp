#include "gen/Animal.hpp"
#include "testframework.hpp"
#include "testutils.hpp"
#include <QSignalSpy>

namespace ObjectInInterface {
using namespace qtgql;

auto ENV_NAME = std::string("ObjectInInterface");
auto SCHEMA_ADDR = get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("ObjectInInterface") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") {
    auto animal_query = animal::Animal::shared();
    animal_query->set_variables({Enums::AnimalKind::DOG});
    animal_query->fetch();
    test_utils::wait_for_completion(animal_query);
    auto animal = animal_query->data()->get_animal();
    REQUIRE(animal->get_metadata()->get_kind() == Enums::AnimalKind::DOG);
    auto dog = qobject_cast<const animal::Dog__animal *>(animal);
    REQUIRE(!dog->get_furColor().isEmpty());
  };
}

}; // namespace ObjectInInterface
