#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
namespace ScalarsTestCase {
using namespace qtgql;
auto ENV_NAME = QString("ScalarsTestCase");
auto SCHEMA_ADDR = get_server_address("97455992");

TEST_CASE("ScalarsTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  SECTION("test scalar types and deserialization") {
    REQUIRE(QTest::qWaitFor([&]() -> bool { return mq->completed(); }, 1500));
    auto d = mq->get_data();
    REQUIRE(d->get_age() == 24);
    REQUIRE(d->get_agePoint() == 24.0f);
    REQUIRE(d->get_id() == "FakeID");
    REQUIRE(d->get_male() == true);
    REQUIRE(d->get_name() == "nir");
    REQUIRE(d->get_uuid() ==
            QUuid::fromString("06335e84-2872-4914-8c5d-3ed07d2a2f16\""));
  };
};
};  // namespace ScalarsTestCase
