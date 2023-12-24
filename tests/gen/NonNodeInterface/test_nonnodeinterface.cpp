#include "gen/AnimalQuery.hpp"
#include "gen/ChangeAgeMutation.hpp"
#include "testframework.hpp"
#include "testutils.hpp"
#include <QSignalSpy>

namespace NonNodeInterface {
using namespace qtgql;

auto ENV_NAME = std::string("NonNodeInterface");
auto SCHEMA_ADDR =
    test_utils::get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("NonNodeInterface") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME,
      test_utils::DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto animal_query = animalquery::AnimalQuery::shared();
  animal_query->set_variables({NonNodeInterface::Enums::AnimalKind::DOG});
  animal_query->fetch();
  test_utils::wait_for_completion(animal_query);
  SECTION("test deserialize") {
    auto animal = animal_query->data()->get_animal();
    REQUIRE(animal->get_kind() == NonNodeInterface::Enums::AnimalKind::DOG);
    auto dog = qobject_cast<const animalquery::Dog__animal *>(animal);
    REQUIRE(!dog->get_furColor().isEmpty());
  };
  SECTION("test updates new type") {
    auto root = animal_query->data();
    animal_query->set_variables({NonNodeInterface::Enums::AnimalKind::PERSON});
    test_utils::SignalCatcher catcher({.source_obj = root, .only = "animal"});
    animal_query->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(animal_query);
    REQUIRE(animal_query->data()->get_animal()->get_kind() ==
            NonNodeInterface::Enums::PERSON);
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
    test_utils::SignalCatcher catcher(
        {.source_obj = change_age_mut->data(), .only = "changeAge"});
    change_age_mut->set_variables({animal_id, new_age});
    change_age_mut->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(change_age_mut);
    REQUIRE(change_age_mut->data()->get_changeAge()->get_age() == new_age);
  }
}

}; // namespace NonNodeInterface
