#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"

namespace ObjectWithListOfObjectTestCase {
using namespace qtgql;

TEST_CASE("ObjectWithListOfObjectTestCase", "[generated-testcase]") {
  auto addr = get_server_address("89749059");
  auto env = std::make_shared<bases::Environment>(
      "ObjectWithListOfObjectTestCase",
      std::unique_ptr<qtgql::gqlwstransport::GqlWsTransportClient>(
          new DebugAbleClient(
              DebugClientSettings{.prod_settings = {.url = addr}})));
  bases::Environment::set_gql_env(env);
  DebugAbleClient::from_environment(env)->wait_for_valid();

  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test gets data") {
    auto persons = mq->get_data()->get_persons();
    auto p = persons->first();
    qDebug() << p->get_name();
    REQUIRE(p->get_name() != bases::DEFAULTS::STRING);
  }

  SECTION(
      "default ListModelABC modifications and operations (not specific to this "
      "testcase)") {
    typedef qtgql::bases::ListModelABC<mainquery::Person__age$id$name>
        ModelType;
    typedef mainquery::Person__age$id$name ObjectType;

    auto model_with_data = mq->get_data()->m_persons;
    auto raw_message =
        DebugAbleClient::from_environment(env)->m_current_message;
    auto persons_raw = raw_message.value()
                           .payload.value("data")
                           .toObject()
                           .value("persons")
                           .toArray();

    QSignalSpy p_pre_remove(model_with_data, &ModelType::rowsAboutToBeRemoved);
    QSignalSpy p_after_remove(model_with_data, &ModelType::rowsRemoved);
    test_utils::CompleteSpy remove_spy(&p_pre_remove, &p_after_remove);
    QSignalSpy p_pre_insert(model_with_data, &ModelType::rowsAboutToBeInserted);
    QSignalSpy p_after_insert(model_with_data, &ModelType::rowsInserted);
    test_utils::CompleteSpy insert_spy(&p_pre_insert, &p_after_insert);

    SECTION("object role is USER_ROLE + 1") {
      int expected = Qt::UserRole + 1;
      auto roles = model_with_data->roleNames();
      REQUIRE(roles.value(expected) == QByteArray("qtObject"));
    }
    SECTION("test row count") {
      REQUIRE(model_with_data->rowCount() == persons_raw.size());
    }

    SECTION("test returns data") {
      auto res = model_with_data->data(model_with_data->index(0),
                                       ModelType ::QOBJECT_ROLE);
      REQUIRE(res.canConvert<ObjectType>());
      auto v = res.value<ObjectType*>();
      REQUIRE(v->get_name() ==
              persons_raw.at(0).toObject().value("name").toString());
    }

    SECTION("test pop") {
      model_with_data->pop();
      REQUIRE(model_with_data->rowCount() == persons_raw.size() - 1);
      auto val =
          model_with_data->get(model_with_data->rowCount() - 1)->get_name();
      auto val2 = persons_raw.at(model_with_data->rowCount() - 1)
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
      REQUIRE(model_with_data->rowCount() == 3);
      auto first_item = model_with_data->first();
      REQUIRE(model_with_data->removeRows(1, model_with_data->rowCount() - 1));
      remove_spy.validate();
      REQUIRE(model_with_data->rowCount() == 1);
      auto new_last = model_with_data->first();
      REQUIRE(new_last->get_name() == first_item->get_name());
    }

    SECTION("test append") {
      auto new_obj = new mainquery::Person__age$id$name(nullptr, {});
      auto before_count = model_with_data->rowCount();
      model_with_data->append(new_obj);
      insert_spy.validate();
      auto after_count = model_with_data->rowCount();
      REQUIRE(before_count == after_count - 1);
      REQUIRE(model_with_data->last() == new_obj);
    }
    SECTION("test insert") {
      auto new_obj = new mainquery::Person__age$id$name(nullptr, {});
      auto before_count = model_with_data->rowCount();
      model_with_data->insert(0, new_obj);
      insert_spy.validate();
      auto after_count = model_with_data->rowCount();
      REQUIRE(before_count == after_count - 1);
      REQUIRE(model_with_data->first() == new_obj);
    }
    SECTION("test insert after max index") {
      QSignalSpy spy(model_with_data, &ModelType ::rowsAboutToBeInserted);
      auto new_obj = new mainquery::Person__age$id$name(nullptr, {});
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
}

};  // namespace ObjectWithListOfObjectTestCase
