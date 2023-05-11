#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "fooobjectwithid.h"

TEST_CASE("Test QtGqlObjectTypeABCWithID", "[templates]") {
  auto a =
      std::make_shared<qtgql::NodeRecord<Foo>>(std::make_shared<Foo>("fooid"));
  SECTION("can add to store") {
    Foo::__store__().add_record(a);
    REQUIRE(Foo::__store__()
                .get_record(a->node->get_id())
                .value()
                ->node->get_id() == "fooid");
  }
}
