#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "fooqobject.hpp"
#include "qgraphqllistmodel.hpp"

typedef std::shared_ptr<FooQObject> SharedFoo;

class SampleQGraphQLListModel : public qtgql::QGraphQLListModelABC<SharedFoo> {
  void update(const QList<QJsonObject>& data,
              const SelectionsConfig& selections) override {
    std::ignore = data;
    std::ignore = selections;
  }
  using qtgql::QGraphQLListModelABC<SharedFoo>::QGraphQLListModelABC;
};

TEST_CASE("default QGraphQLListModelABC modifications and operations",
          "[qgraphqllistmodle-raw]") {
  std::unique_ptr<std::vector<int>> a = std::make_unique<std::vector<int>>();
  std::unique_ptr<QList<SharedFoo>> init_list =
      std::make_unique<QList<SharedFoo>>();
  QList<SharedFoo> init_list_copy;
  for (const auto& a : {"foo", "bar", "baz"}) {
    auto obj = std::make_shared<FooQObject>(a);
    init_list->append(obj);
    init_list_copy.append(obj);
  }
  auto model_with_data = SampleQGraphQLListModel{nullptr, std::move(init_list)};

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
                                    SampleQGraphQLListModel::QOBJECT_ROLE);
    REQUIRE(res.canConvert<FooQObject>());
    auto v = res.value<FooQObject*>();
    REQUIRE(v->val == init_list_copy.value(0)->val);
  }

  SECTION("test pop") { QSignalSpy spy(box, SIGNAL(clicked(bool))); }
}
