#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"

namespace ObjectWithListOfObjectTestCase {
using namespace qtgql;
auto ENV_NAME = QString("ObjectWithListOfObjectTestCase");
auto SCHEMA_ADDR = get_server_address("89749059");

TEST_CASE("ObjectWithListOfObjectTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    auto persons = mq->get_data()->get_persons();
    auto p = persons->first();
    qDebug() << p->get_name();
    REQUIRE(p->get_name() != bases::DEFAULTS::STRING);
  }
}

TEST_CASE(
    "default ListModelABC modifications and operations (not specific to this "
    "testcase)",
    "") {
  //    test_utils::ModelSignalSpy
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = std::make_shared<mainquery::MainQuery>();
  auto operation_metadata = mq->operation_metadata();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  typedef qtgql::bases::ListModelABC<mainquery::Person__age$id$name> ModelType;
  typedef mainquery::Person__age$id$name ObjectType;

  auto model_with_data = mq->get_data()->m_persons;
  auto raw_message = DebugAbleClient::from_environment(env)->m_current_message;
  auto raw_persons_list = raw_message.value("data")
                              .toObject()
                              .value("user")
                              .toObject()
                              .value("persons")
                              .toArray();
  QSignalSpy p_pre_remove(model_with_data, &ModelType::rowsAboutToBeRemoved);
  QSignalSpy p_after_remove(model_with_data, &ModelType::rowsRemoved);
  test_utils::ModelSignalSpy remove_spy(&p_pre_remove, &p_after_remove);
  QSignalSpy p_pre_insert(model_with_data, &ModelType::rowsAboutToBeInserted);
  QSignalSpy p_after_insert(model_with_data, &ModelType::rowsInserted);
  test_utils::ModelSignalSpy insert_spy(&p_pre_insert, &p_after_insert);

  SECTION("object role is USER_ROLE + 1") {
    int expected = Qt::UserRole + 1;
    auto roles = model_with_data->roleNames();
    REQUIRE(roles.value(expected) == QByteArray("qtObject"));
  }

  SECTION("test row count") {
    REQUIRE(model_with_data->rowCount() == raw_persons_list.size());
  }

  SECTION("test returns data") {
    auto res = model_with_data->data(model_with_data->index(0),
                                     ModelType ::QOBJECT_ROLE);
    REQUIRE(res.canConvert<ObjectType>());
    auto v = res.value<ObjectType*>();
    REQUIRE(v->get_name() ==
            raw_persons_list.at(0).toObject().value("name").toString());
  }

  SECTION("test pop") {
    model_with_data->pop();
    REQUIRE(model_with_data->rowCount() == raw_persons_list.size() - 1);
    auto val =
        model_with_data->get(model_with_data->rowCount() - 1)->get_name();
    auto val2 = raw_persons_list.at(model_with_data->rowCount() - 1)
                    .toObject()
                    .value("name")
                    .toString();
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
    auto new_obj =
        new mainquery::Person__age$id$name(mq.get(), {}, operation_metadata);
    auto before_count = model_with_data->rowCount();
    model_with_data->append(new_obj);
    insert_spy.validate();
    auto after_count = model_with_data->rowCount();
    REQUIRE(before_count == after_count - 1);
    REQUIRE(model_with_data->last() == new_obj);
  }
  SECTION("test insert") {
    auto new_obj =
        new mainquery::Person__age$id$name(mq.get(), {}, operation_metadata);
    auto before_count = model_with_data->rowCount();
    model_with_data->insert(0, new_obj);
    insert_spy.validate();
    auto after_count = model_with_data->rowCount();
    REQUIRE(before_count == after_count - 1);
    REQUIRE(model_with_data->first() == new_obj);
  }
  SECTION("test insert after max index") {
    QSignalSpy spy(model_with_data, &ModelType ::rowsAboutToBeInserted);
    auto new_obj =
        new mainquery::Person__age$id$name(mq.get(), {}, operation_metadata);
    auto before_count = model_with_data->rowCount();
    model_with_data->insert(20000, new_obj);
    insert_spy.validate();
    auto after_count = model_with_data->rowCount();
    REQUIRE(before_count == after_count - 1);
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
}  // namespace ObjectWithListOfObjectTestCase
