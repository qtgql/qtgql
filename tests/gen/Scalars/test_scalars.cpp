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
auto SCHEMA_ADDR = get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("Scalars") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);

  SECTION("test deserialize") {
    auto d = mq->data()->get_constUser();
    REQUIRE_EQ(d->get_age() , 24);
    REQUIRE_EQ(d->get_agePoint() , 24.0f);
    REQUIRE_EQ(d->get_id() , "FakeID");
    REQUIRE_EQ(d->get_male() , true);
    REQUIRE_EQ(d->get_name() , "nir");
    REQUIRE_EQ(d->get_uuid() ,
            QUuid::fromString("06335e84-2872-4914-8c5d-3ed07d2a2f16"));
    REQUIRE_EQ(d->get_voidField() , qtgql::bases::DEFAULTS::VOID);
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
    REQUIRE_EQ(user->get_id() , modified_user->get_id());
    auto new_name = modified_user->get_name();
    REQUIRE_EQ(user->get_name() , new_name);
    REQUIRE_NE(new_name , previous_name);
  };
};

}; // namespace Scalars
