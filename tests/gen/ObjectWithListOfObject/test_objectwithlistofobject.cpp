#include "testframework.hpp"
#include <QSignalSpy>

#include "gen/AddFriend.hpp"
#include "gen/MainQuery.hpp"
#include "testutils.hpp"

namespace ObjectWithListOfObject {
using namespace qtgql;
auto ENV_NAME = std::string("ObjectWithListOfObject");
auto SCHEMA_ADDR = get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("ObjectWithListOfObject") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = mainquery::MainQuery::shared();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    auto friends = mq->data()->get_user()->get_friends();
    auto p = friends->first();
    REQUIRE_NE(p->get_name() , bases::DEFAULTS::STRING);
  }
  SECTION("test update") {
    auto add_friend_mut = addfriend::AddFriend::shared();
    QString new_name("Momo");
    auto mq_model = mq->data()->get_user()->get_friends();
    auto before_count = mq_model->rowCount();
    add_friend_mut->set_variables({mq->data()->get_user()->get_id(), new_name});
    add_friend_mut->fetch();
    test_utils::wait_for_completion(add_friend_mut);
    // add friend mutation will add friend to the user with name X
    // when the updated user data returns from the mutation, the list on the
    // main query should update as well with a new friend.
    REQUIRE(before_count < mq_model->rowCount());
    REQUIRE_EQ(mq_model->rowCount() ,
            add_friend_mut->data()->get_addFriend()->get_friends()->rowCount());
  }
}

} // namespace ObjectWithListOfObject
