#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include "graphql/__generated__/UserWithSameIDAndDifferentFieldsQuery.hpp"

namespace ScalarsTestCase {
using namespace qtgql;
auto ENV_NAME = QString("ScalarsTestCase");
auto SCHEMA_ADDR = get_server_address("76177312");

TEST_CASE("ScalarsTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);

  SECTION("test deserialize") {
    auto d = mq->data()->get_constUser();
    REQUIRE(d->get_age() == 24);
    REQUIRE(d->get_agePoint() == 24.0f);
    REQUIRE(d->get_id() == "FakeID");
    REQUIRE(d->get_male() == true);
    REQUIRE(d->get_name() == "nir");
    REQUIRE(d->get_uuid() ==
            QUuid::fromString("06335e84-2872-4914-8c5d-3ed07d2a2f16"));
    REQUIRE(d->get_voidField() == qtgql::bases::DEFAULTS::VOID);
  };
  SECTION("test update") {

    auto data = mq->data();
    auto user = data->get_constUser();
    auto previous_name = user->get_name();
    auto modified_user_op = userwithsameidanddifferentfieldsquery::
        UserWithSameIDAndDifferentFieldsQuery::shared();
    auto catcher = test_utils::SignalCatcher({user});
    modified_user_op->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(modified_user_op);
    auto modified_user =
        modified_user_op->data()->get_constUserWithModifiedFields();
    REQUIRE(user->get_id() == modified_user->get_id());
    auto new_name = modified_user->get_name();
    REQUIRE(user->get_name() == new_name);
    REQUIRE(new_name != previous_name);
  };
};

std::shared_ptr<ScalarsTestCase::User> get_shared_user() {
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  auto node_id = mq->data()->get_constUser()->get_id();
  REQUIRE(mq.use_count() == 1);
  return ScalarsTestCase::User::get_node(node_id).value();
}

using namespace std::chrono_literals;

TEST_CASE("Test Garbage collection") {

  auto env = test_utils::get_or_create_env(
      ENV_NAME,
      DebugClientSettings{.prod_settings =
                              {
                                  .url = SCHEMA_ADDR,
                              }},
      100ms);
  std::weak_ptr<ScalarsTestCase::User> weak_user = get_shared_user();
  ScalarsTestCase::Query::instance()->m_constUser = {};
  // at map
  REQUIRE(weak_user.use_count() == 1);
  REQUIRE(QTest::qWaitFor([&]() { return weak_user.use_count() == 0; }));
}

}; // namespace ScalarsTestCase
