#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "fooqobject.hpp"
#include "qtgql/bases/bases.hpp"

typedef std::shared_ptr<FooQObject> SharedFoo;
using namespace qtgql;

typedef bases::ListModelABC<FooQObject> SampleGraphQLListModel;

struct CompleteSpy {
  QSignalSpy* about_to;
  QSignalSpy* after;
  explicit CompleteSpy(QSignalSpy* about, QSignalSpy* _after)
      : about_to{about}, after{_after} {
    REQUIRE(about->isEmpty());
    REQUIRE(after->isEmpty());
  }

  void validate() {
    REQUIRE(!about_to->isEmpty());
    REQUIRE(!after->isEmpty());
  }
};

TEST_CASE("default GraphQLListModelABC modifications and operations",
          "[qgraphqllistmodle-raw]") {
  std::unique_ptr<std::vector<int>> a = std::make_unique<std::vector<int>>();
  std::unique_ptr<QList<SharedFoo>> __init_list =
      std::make_unique<QList<SharedFoo>>();
  QList<SharedFoo> init_list_copy;
  for (const auto& a : {"foo", "bar", "baz"}) {
    auto obj = std::make_shared<FooQObject>(a);
    __init_list->append(obj);
    init_list_copy.append(obj);
  }
  auto model_with_data =
      SampleGraphQLListModel{nullptr, std::move(__init_list)};
  QSignalSpy p_pre_remove(&model_with_data,
                          &SampleGraphQLListModel::rowsAboutToBeRemoved);
  QSignalSpy p_after_remove(&model_with_data,
                            &SampleGraphQLListModel::rowsRemoved);
  CompleteSpy remove_spy(&p_pre_remove, &p_after_remove);
  QSignalSpy p_pre_insert(&model_with_data,
                          &SampleGraphQLListModel::rowsAboutToBeInserted);
  QSignalSpy p_after_insert(&model_with_data,
                            &SampleGraphQLListModel::rowsInserted);
  CompleteSpy insert_spy(&p_pre_insert, &p_after_insert);

  SECTION("object role is USER_ROLE + 1") {
    int expected = Qt::UserRole + 1;
    auto roles = model_with_data.roleNames();
    REQUIRE(roles.value(expected) == QByteArray("qtObject"));
  }
  SECTION("test row count") {
    REQUIRE(model_with_data.rowCount() == init_list_copy.length());
  }

  SECTION("test returns data") {
    auto res = model_with_data.data(model_with_data.index(0),
                                    SampleGraphQLListModel::QOBJECT_ROLE);
    REQUIRE(res.canConvert<FooQObject>());
    auto v = res.value<FooQObject*>();
    REQUIRE(v->val == init_list_copy.value(0)->val);
  }

  SECTION("test pop") {
    model_with_data.pop();
    REQUIRE(model_with_data.rowCount() == init_list_copy.length() - 1);
    auto val = model_with_data.get(model_with_data.rowCount() - 1)->val;
    auto val2 = init_list_copy.value(model_with_data.rowCount() - 1)->val;
    REQUIRE(val == val2);
    remove_spy.validate();
  }

  SECTION("test clear") {
    model_with_data.clear();
    remove_spy.validate();
    REQUIRE(model_with_data.rowCount() == 0);
  }
  SECTION("test remove rows") {
    model_with_data.removeRows(0, model_with_data.rowCount());
    REQUIRE(model_with_data.rowCount() == 0);
    remove_spy.validate();
  }
  SECTION("test remove rows inside") {
    REQUIRE(model_with_data.rowCount() == 3);
    auto first_item = model_with_data.first();
    REQUIRE(model_with_data.removeRows(1, model_with_data.rowCount() - 1));
    remove_spy.validate();
    REQUIRE(model_with_data.rowCount() == 1);
    auto new_last = model_with_data.first();
    REQUIRE(new_last.get() == first_item.get());
  }

  SECTION("test append") {
    auto new_obj = std::make_shared<FooQObject>("zib");
    auto before_count = model_with_data.rowCount();
    model_with_data.append(new_obj);
    insert_spy.validate();
    auto after_count = model_with_data.rowCount();
    REQUIRE(before_count == after_count - 1);
    REQUIRE(model_with_data.last().get() == new_obj.get());
  }
  SECTION("test insert") {
    auto new_obj = std::make_shared<FooQObject>("zib");
    auto before_count = model_with_data.rowCount();
    model_with_data.insert(0, new_obj);
    insert_spy.validate();
    auto after_count = model_with_data.rowCount();
    REQUIRE(before_count == after_count - 1);
    REQUIRE(model_with_data.first().get() == new_obj.get());
  }
  SECTION("test insert after max index") {
    QSignalSpy spy(&model_with_data,
                   &SampleGraphQLListModel::rowsAboutToBeInserted);
    auto new_obj = std::make_shared<FooQObject>("zib");
    auto before_count = model_with_data.rowCount();
    model_with_data.insert(20000, new_obj);
    insert_spy.validate();
    auto after_count = model_with_data.rowCount();
    REQUIRE(before_count == after_count - 1);
    REQUIRE(model_with_data.last().get() == new_obj.get());
  }

  SECTION("test current index prop") {
    bool ok = false;
    REQUIRE(model_with_data.property("currentIndex").toInt(&ok) == 0);
    REQUIRE(ok);
  }

  SECTION("test current index emits on set") {
    QSignalSpy spy(&model_with_data,
                   &SampleGraphQLListModel::currentIndexChanged);
    model_with_data.set_current_index(2);
    REQUIRE(!spy.isEmpty());
    bool ok = false;
    REQUIRE(model_with_data.property("currentIndex").toInt(&ok) == 2);
    REQUIRE(ok);
  }
}
