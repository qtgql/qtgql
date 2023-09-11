#include "gen/InsertToList.hpp"
#include "gen/MainQuery.hpp"
#include "gen/ModifyName.hpp"
#include "gen/RemoveAt.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace ListOfUnion {
using namespace qtgql;

auto ENV_NAME = std::string("ListOfUnion");
auto SCHEMA_ADDR = get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("ListOfUnion", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.print_debug = true,
                                    .prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = mainquery::MainQuery::shared();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    auto root = mq->data();
    auto model = root->get_randPerson()->get_pets();
    auto union_data = model->first();
    auto type_name = union_data->__typename();
    if (type_name == "Cat") {
      REQUIRE(!qobject_cast<mainquery::Cat__randPersonpets *>(union_data)
                   ->get_color()
                   .isEmpty());
    } else {
      REQUIRE(qobject_cast<mainquery::Dog__randPersonpets *>(union_data)
                  ->get_age() > 0);
    }
  };

  SECTION("test update modify") {
    auto modify_mut = modifyname::ModifyName::shared();
    auto person = mq->data()->get_randPerson();
    auto model = person->get_pets();
    QString new_name("Frank Zappa");
    modify_mut->set_variables({person->get_id(), 3, new_name});
    modify_mut->fetch();
    test_utils::wait_for_completion(modify_mut);
    REQUIRE(model->get(3)->property("name").toString().toStdString() ==
            new_name.toStdString());
  }
  SECTION("test update add") {
    auto insert_mut = inserttolist::InsertToList::shared();
    auto person = mq->data()->get_randPerson();
    auto model = person->get_pets();
    QString name_to_set("Abu Nasr al-Farabi");
    auto prev_length = model->rowCount();
    insert_mut->set_variables({person->get_id(), prev_length + 1, name_to_set,
                               ListOfUnion::Enums::UnionTypes::DOG});
    insert_mut->fetch();
    test_utils::wait_for_completion(insert_mut);
    REQUIRE(prev_length < model->rowCount());
    qDebug() << model->last();
    auto dog =
        qobject_cast<const mainquery::Dog__randPersonpets *>(model->last());
    REQUIRE(dog->__typename().toStdString() == "Dog");
    REQUIRE(dog->get_name().toStdString() == name_to_set.toStdString());
  }
  SECTION("test update remove") {
    auto person = mq->data()->get_randPerson();
    auto model = person->get_pets();
    auto obj_at_3 = model->get(3);
    QString name_for_third_item("");
    if (auto dog = qobject_cast<mainquery::Dog__randPersonpets *>(obj_at_3)) {
      name_for_third_item = dog->get_name();
    } else {
      auto cat = qobject_cast<mainquery::Cat__randPersonpets *>(obj_at_3);
      name_for_third_item = cat->get_name();
    }
    REQUIRE(!name_for_third_item.isEmpty());

    auto remove_mut = removeat::RemoveAt::shared();
    remove_mut->set_variables({person->get_id(), 3});
    remove_mut->fetch();

    test_utils::wait_for_completion(remove_mut);

    REQUIRE(model->get(3)->property("name").toString().toStdString() !=
            name_for_third_item.toStdString());
  };
}

}; // namespace ListOfUnionTestCase
