#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/AnimalQuery.hpp"
#include "graphql/__generated__/ChangeAgeMutation.hpp"

namespace InterfaceTestCase {
using namespace qtgql;

auto ENV_NAME = QString("InterfaceTestCase");
auto SCHEMA_ADDR = get_server_address("32048780");

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
    auto dog = qobject_cast<const animalquery::Dog__animal *>(animal);
    REQUIRE(!dog->get_furColor().isEmpty());
  };
  SECTION("test updates new type") {
    auto root = animal_query->data();
    animal_query->set_variables({InterfaceTestCase::Enums::AnimalKind::PERSON});
    test_utils::SignalCatcher catcher({.source_obj = root, .only = "animal"});
    animal_query->refetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(animal_query);
    REQUIRE(animal_query->data()->get_animal()->get_kind() ==
            InterfaceTestCase::Enums::PERSON);
    auto person = qobject_cast<const animalquery::Person__animal *>(
        animal_query->data()->get_animal());
    REQUIRE(!person->get_language().isEmpty());
  }

  SECTION("test updates same type") {
    auto change_age_mut = changeagemutation::ChangeAgeMutation::shared();
    // since this is not implementing node, first get the data filled on that
    // field
    auto animal_id = animal_query->data()->get_animal()->get_id();
    change_age_mut->set_variables({animal_id, 156});
    change_age_mut->fetch();
    test_utils::wait_for_completion(change_age_mut);
    // now we can test the update.
    int new_age = 2223432;
    change_age_mut->set_variables({animal_id, new_age});
    change_age_mut->refetch();
    test_utils::wait_for_completion(change_age_mut);
    // TODO: check signals emission here...
    REQUIRE(change_age_mut->data()->get_changeAge()->get_age() == new_age);
  }
}

}; // namespace InterfaceTestCase
