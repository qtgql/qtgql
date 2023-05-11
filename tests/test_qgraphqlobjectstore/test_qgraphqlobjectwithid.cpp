#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "fooobjectwithid.h"

TEST_CASE("Test QGraphQLObjectStore", "[templates]") {
  auto tested_obj = std::make_shared<Foo>("fooid");
  auto obj_record = std::make_shared<qtgql::NodeRecord<Foo>>(tested_obj);
  SECTION("can add to store") {
    Foo::__store__().add_record(obj_record);
    REQUIRE(Foo::__store__()
                .get_record(obj_record->node->get_id())
                .value()
                ->node->get_id() == tested_obj->get_id());
  }

  SECTION("get_id() with wrong id returns empty optional") {
    auto optional_foo = Foo::__store__().get_record("wrong id");
    REQUIRE(!optional_foo);
  }
}
