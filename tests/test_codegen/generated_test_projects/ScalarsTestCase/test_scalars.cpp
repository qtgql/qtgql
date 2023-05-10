//#include <QSignalSpy>
//#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "./graphql/__generated__/MainQuery.hpp"

TEST_CASE("sample") {
  auto query = mainquery::User__age$agePoint$id$male$name$uuid();
  REQUIRE(1 == 1);
}
