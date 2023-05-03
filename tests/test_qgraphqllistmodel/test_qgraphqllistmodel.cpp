#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "qgraphqllistmodel.hpp"

class SampleQGraphQLListModelABC
    : public qtgql::QGraphQLListModelABC<std::shared_ptr<QObject>> {
  void update(const QList<QJsonObject>& data,
              const SelectionsConfig& selections) override {
    std::ignore = data;
    std::ignore = selections;
  }
};

TEST_CASE("default QGraphQLListModelABC modifications and operations") {
  auto a = SampleQGraphQLListModelABC{};
}
