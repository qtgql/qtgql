#include "testframework.hpp"
#include "testutils.hpp"
#include <qtgql/bases/bases.hpp>
using namespace qtgql;

TEST_CASE("ListModelABC modifications and operations") {
  test_utils::QCleanerObject parent_cleaner(nullptr);

  std::vector<QObject *> init_vec;
  for (int i = 0; i < 10; i++) {
    init_vec.emplace_back(new QObject(&parent_cleaner));
  }

  typedef bases::ListModelABC<QObject *> ModelType;
  auto model_with_data = ModelType(nullptr, init_vec);

  QSignalSpy p_pre_remove(&model_with_data, &ModelType::rowsAboutToBeRemoved);
  QSignalSpy p_after_remove(&model_with_data, &ModelType::rowsRemoved);
  test_utils::ModelSignalSpy remove_spy(&p_pre_remove, &p_after_remove);
  QSignalSpy p_pre_insert(&model_with_data, &ModelType::rowsAboutToBeInserted);
  QSignalSpy p_after_insert(&model_with_data, &ModelType::rowsInserted);
  test_utils::ModelSignalSpy insert_spy(&p_pre_insert, &p_after_insert);

  SECTION("data role is USER_ROLE + 1") {
    int expected = Qt::UserRole + 1;
    auto roles = model_with_data.roleNames();
    REQUIRE_EQ(roles.value(expected) , QByteArray("data"));
  }

  SECTION("test row count") {
    REQUIRE_EQ(model_with_data.rowCount() , init_vec.size());
  }

  SECTION("test returns data") {

    init_vec[0]->setProperty("name", "foobar");
    auto res =
        model_with_data.data(model_with_data.index(0), ModelType ::DATA_ROLE);
    REQUIRE(res.canConvert<QObject *>());
    REQUIRE_EQ(res.value<QObject *>()->property("name").toString().toStdString() ,
            "foobar");
  }

  SECTION("test pop") {
    qDebug() << "Before";
    qDebug() << "First: " << model_with_data.first();
    qDebug() << "Last: " << model_with_data.last();
    model_with_data.pop();
    qDebug() << "After";
    qDebug() << "First: " << model_with_data.first();
    qDebug() << "Last: " << model_with_data.last();
    REQUIRE_EQ(model_with_data.rowCount() , init_vec.size() - 1);
    auto val = model_with_data.last();
    auto val2 = init_vec.at(model_with_data.rowCount() - 1);
    REQUIRE_EQ(val , val2);
    remove_spy.validate();
  }

  SECTION("test clear") {
    model_with_data.clear();
    remove_spy.validate();
    REQUIRE_EQ(model_with_data.rowCount() , 0);
  }
  SECTION("test remove rows") {
    model_with_data.removeRows(0, model_with_data.rowCount());
    REQUIRE_EQ(model_with_data.rowCount() , 0);
    remove_spy.validate();
  }
  SECTION("test remove rows inside") {
    REQUIRE_EQ(model_with_data.rowCount() , 10);
    auto first_item = model_with_data.first();
    REQUIRE(model_with_data.removeRows(1, model_with_data.rowCount() - 1));
    remove_spy.validate();
    REQUIRE_EQ(model_with_data.rowCount() , 1);
    auto new_last = model_with_data.first();
    REQUIRE_EQ(new_last , first_item);
  }

  auto new_obj = new QObject(&parent_cleaner);

  SECTION("test append") {
    auto before_count = model_with_data.rowCount();
    model_with_data.append(new_obj);
    insert_spy.validate();
    auto after_count = model_with_data.rowCount();
    REQUIRE_EQ(before_count , after_count - 1);
    REQUIRE_EQ(model_with_data.last() , new_obj);
  }
  SECTION("test replace") {

    auto before_count = model_with_data.rowCount();
    model_with_data.replace(model_with_data.rowCount() - 1, new_obj);
    insert_spy.validate();
    auto after_count = model_with_data.rowCount();
    REQUIRE_EQ(before_count , after_count);
    REQUIRE_EQ(model_with_data.last() , new_obj);
  }

  SECTION("test current index prop") {
    bool ok = false;
    REQUIRE_EQ(model_with_data.property("currentIndex").toInt(&ok) , 0);
    REQUIRE(ok);
  }

  SECTION("test current index emits on set") {
    QSignalSpy spy(&model_with_data, &ModelType::currentIndexChanged);
    model_with_data.set_current_index(2);
    REQUIRE(!spy.isEmpty());
    bool ok = false;
    REQUIRE_EQ(model_with_data.property("currentIndex").toInt(&ok) , 2);
    REQUIRE(ok);
  }
}
