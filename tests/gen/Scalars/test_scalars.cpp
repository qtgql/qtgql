#include "testframework.hpp"
#include <QSignalSpy>
#include <QTest>

#include "gen/MainQuery.hpp"
#include "gen/UserWithSameIDDiffFields.hpp"
#include "testutils.hpp"

#include "qtgql/gqloverhttp/gqloverhttp.hpp"

namespace Scalars {
using namespace qtgql;
auto ENV_NAME = std::string("Scalars");
auto SCHEMA_ADDR = test_utils::get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("Scalars") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, test_utils::DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
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
    auto modified_user_op =
        userwithsameiddifffields::UserWithSameIDDiffFields::shared();
    auto catcher = test_utils::SignalCatcher(
        {.source_obj = user, .excludes = {{"voidField"}}});
    modified_user_op->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(modified_user_op);
    auto modified_user =
        modified_user_op->data()->get_constUserWithModifiedFields();
    REQUIRE(user->get_id() == modified_user->get_id());
    auto new_name = modified_user->get_name();
    REQUIRE(user->get_name() == new_name);
    REQUIRE(new_name == previous_name);
  };
};

}; // namespace Scalars
