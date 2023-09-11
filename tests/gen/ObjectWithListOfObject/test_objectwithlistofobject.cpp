#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "gen/AddFriend.hpp"
#include "gen/MainQuery.hpp"
#include "testutils.hpp"

namespace ObjectWithListOfObject {
using namespace qtgql;
auto ENV_NAME = std::string("ObjectWithListOfObjectTestCase");
auto SCHEMA_ADDR = get_server_address("ObjectWithListOfObjectTestCase");

TEST_CASE("ObjectWithListOfObjectTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = mainquery::MainQuery::shared();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    auto friends = mq->data()->get_user()->get_friends();
    auto p = friends->first();
    REQUIRE(p->get_name() != bases::DEFAULTS::STRING);
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
    REQUIRE(mq_model->rowCount() ==
            add_friend_mut->data()->get_addFriend()->m_friends->rowCount());
  }
}

TEST_CASE("default ListModelABC modifications and operations",
          "[listmodel testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  typedef mainquery::Person__userfriends ObjectType;
  typedef qtgql::bases::ListModelABC<ObjectType> ModelType;

  auto model_with_data = mq->data()->get_user()->m_friends;
  auto raw_message =
      DebugAbleWsNetworkLayer::from_environment(env)->m_current_message;
  auto raw_friends_list = raw_message.value("data")
                              .toObject()
                              .value("user")
                              .toObject()
                              .value("friends")
                              .toArray();
  QSignalSpy p_pre_remove(model_with_data, &ModelType::rowsAboutToBeRemoved);
  QSignalSpy p_after_remove(model_with_data, &ModelType::rowsRemoved);
  test_utils::ModelSignalSpy remove_spy(&p_pre_remove, &p_after_remove);
  QSignalSpy p_pre_insert(model_with_data, &ModelType::rowsAboutToBeInserted);
  QSignalSpy p_after_insert(model_with_data, &ModelType::rowsInserted);
  test_utils::ModelSignalSpy insert_spy(&p_pre_insert, &p_after_insert);

  SECTION("data role is USER_ROLE + 1") {
    int expected = Qt::UserRole + 1;
    auto roles = model_with_data->roleNames();
    REQUIRE(roles.value(expected) == QByteArray("data"));
  }

  SECTION("test row count") {
    REQUIRE(model_with_data->rowCount() == raw_friends_list.size());
  }

  SECTION("test returns data") {
    auto res =
        model_with_data->data(model_with_data->index(0), ModelType ::DATA_ROLE);
    REQUIRE(res.canConvert<ObjectType>());
    auto v = res.value<ObjectType *>();
    REQUIRE(v->get_name() ==
            raw_friends_list.at(0).toObject().value("name").toString());
  }

  SECTION("test pop") {
    qDebug() << "Before";
    qDebug() << "First: " << model_with_data->first()->get_name().toStdString();
    qDebug() << "Last: " << model_with_data->last()->get_name().toStdString();
    model_with_data->pop();
    qDebug() << "After";
    qDebug() << "First: " << model_with_data->first()->get_name().toStdString();
    qDebug() << "Last: " << model_with_data->last()->get_name().toStdString();
    REQUIRE(model_with_data->rowCount() == raw_friends_list.size() - 1);
    auto val = model_with_data->last()->get_name().toStdString();
    auto val2 = raw_friends_list.at(model_with_data->rowCount() - 1)
                    .toObject()
                    .value("name")
                    .toString()
                    .toStdString();
    REQUIRE(val == val2);
    remove_spy.validate();
  }

  SECTION("test clear") {
    model_with_data->clear();
    remove_spy.validate();
    REQUIRE(model_with_data->rowCount() == 0);
  }
  SECTION("test remove rows") {
    model_with_data->removeRows(0, model_with_data->rowCount());
    REQUIRE(model_with_data->rowCount() == 0);
    remove_spy.validate();
  }
  SECTION("test remove rows inside") {
    REQUIRE(model_with_data->rowCount() == 5);
    auto first_item = model_with_data->first();
    REQUIRE(model_with_data->removeRows(1, model_with_data->rowCount() - 1));
    remove_spy.validate();
    REQUIRE(model_with_data->rowCount() == 1);
    auto new_last = model_with_data->first();
    REQUIRE(new_last->get_name() == first_item->get_name());
  }

  SECTION("test append") {
    auto new_obj = new mainquery::Person__userfriends(
        mq.get(), std::make_shared<ObjectWithListOfObject::Person>());
    auto before_count = model_with_data->rowCount();
    model_with_data->append(new_obj);
    insert_spy.validate();
    auto after_count = model_with_data->rowCount();
    REQUIRE(before_count == after_count - 1);
    REQUIRE(model_with_data->last() == new_obj);
  }
  SECTION("test replace") {
    auto new_obj = new mainquery::Person__userfriends(
        mq.get(), std::make_shared<ObjectWithListOfObject::Person>());
    auto before_count = model_with_data->rowCount();
    model_with_data->replace(model_with_data->rowCount() - 1, new_obj);
    insert_spy.validate();
    auto after_count = model_with_data->rowCount();
    REQUIRE(before_count == after_count);
    REQUIRE(model_with_data->last() == new_obj);
  }

  SECTION("test current index prop") {
    bool ok = false;
    REQUIRE(model_with_data->property("currentIndex").toInt(&ok) == 0);
    REQUIRE(ok);
  }

  SECTION("test current index emits on set") {
    QSignalSpy spy(model_with_data, &ModelType::currentIndexChanged);
    model_with_data->set_current_index(2);
    REQUIRE(!spy.isEmpty());
    bool ok = false;
    REQUIRE(model_with_data->property("currentIndex").toInt(&ok) == 2);
    REQUIRE(ok);
  }
}
} // namespace ObjectWithListOfObjectTestCase
