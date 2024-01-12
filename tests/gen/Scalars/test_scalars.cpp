#include "gen/MainQuery.hpp"
#include "gen/OnlyNameField.hpp"
#include "gen/UserWithSameIDDiffFields.hpp"
#include "testframework.hpp"
#include "testutils.hpp"

#include "qtgql/gqloverhttp/gqloverhttp.hpp"

namespace Scalars {
using namespace qtgql;

TEST_CASE("Scalars") {
  auto ENV_NAME = std::string("Scalars");

  auto SCHEMA_ADDR =
      test_utils::get_server_address(QString::fromStdString(ENV_NAME));
  auto env = test_utils::get_or_create_env(
      ENV_NAME,
      test_utils::DebugWsClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") {
    auto mq = std::make_shared<mainquery::MainQuery>();
    mq->execute();
    test_utils::wait_for_completion(mq);
    auto d = mq->data()->get_constUser();
    REQUIRE(d->get_age() == 24);
    REQUIRE(d->get_agePoint() == 24.0f);
    REQUIRE(d->get_id() == "FakeID");
    REQUIRE(d->get_male() == true);
    REQUIRE(d->get_name() == "nir");
    REQUIRE(d->get_uuid() ==
            QUuid::fromString("06335e84-2872-4914-8c5d-3ed07d2a2f16"));
    REQUIRE(d->get_voidField() == qtgql::bases::DEFAULTS::VOID::value());
  };
  SECTION("test update") {
    auto mq = std::make_shared<mainquery::MainQuery>();
    mq->execute();
    test_utils::wait_for_completion(mq);
    auto data = mq->data();
    auto user = data->get_constUser();
    auto previous_name = user->get_name();
    auto modified_user_op =
        userwithsameiddifffields::UserWithSameIDDiffFields::shared();
    auto catcher = test_utils::SignalCatcher(
        {.source_obj = user, .excludes = {{"voidField"}}});
    modified_user_op->execute();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(modified_user_op);
    auto modified_user =
        modified_user_op->data()->get_constUserWithModifiedFields();
    REQUIRE(user->get_id() == modified_user->get_id());
    auto new_name = modified_user->get_name();
    REQUIRE(user->get_name() == new_name);
    REQUIRE(new_name != previous_name);
  };
  SECTION("test garbage collection") {
    // to test garbage collection, we need to have two
    // operations that each one owning the same object in the object tree,
    // afterward, one operation gets out of scope or deleted, and we should
    // check that the reference count on the fields that was owned by ONLY this
    // operation is cleaned up.
    auto perform_test = [&]() {
      auto mq = std::make_shared<mainquery::MainQuery>();
      mq->execute();
      test_utils::wait_for_completion(mq);
      auto only_name_query = onlynamefield::OnlyNameField::shared();
      only_name_query->execute();
      test_utils::wait_for_completion(only_name_query);
      auto node = env->get_cache()
                      ->get_node(mq->data()->get_constUser()->get_id())
                      ->get();
      auto user = qobject_cast<Scalars::User *>(node);
      REQUIRE(user->m_name.use_count() == 2);
      return only_name_query;
    };
    auto only_name_query = perform_test();
    auto node =
        env->get_cache()
            ->get_node(only_name_query->data()->get_constUser()->get_id())
            ->get();
    auto user = qobject_cast<Scalars::User *>(node);
    REQUIRE(user->m_name.use_count() == 1);
  }
};

}; // namespace Scalars
