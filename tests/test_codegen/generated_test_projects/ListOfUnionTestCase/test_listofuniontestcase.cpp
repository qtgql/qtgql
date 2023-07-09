#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include "graphql/__generated__/ModifyName.hpp"
#include "graphql/__generated__/RemoveAt.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace ListOfUnionTestCase {
using namespace qtgql;

auto ENV_NAME = QString("ListOfUnionTestCase");
auto SCHEMA_ADDR = get_server_address("87764004");

TEST_CASE("ListOfUnionTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
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
  SECTION("test update remove") {
    auto remove_mut = removeat::RemoveAt::shared();
    auto person = mq->data()->get_randPerson();
    auto model = person->get_pets();
    auto name_for_third_item = model->get(3)->property("name").toString();
    REQUIRE(!name_for_third_item.isEmpty());
    remove_mut->set_variables({person->get_id(), 3});
    remove_mut->fetch();
    test_utils::wait_for_completion(remove_mut);
    REQUIRE(model->get(3)->property("name").toString().toStdString() !=
            name_for_third_item.toStdString());
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
}

}; // namespace ListOfUnionTestCase
