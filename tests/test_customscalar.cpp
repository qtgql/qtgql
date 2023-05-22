#include <QString>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "../qtgql/customscalars/qtgqlcustomscalar.hpp"

class CustomStringScalar
    : public qtgql::CustomScalarABC<QString, QString, QString> {
  QString m_cached;

 public:
  const QString &to_qt() override {
    if (m_cached.isEmpty()) {
      m_cached = QString("Decoration-") + m_value;
    }
    return m_cached;
  }
  const QString &GRAPHQL_NAME() override {
    static QString ret = "CustomStringScalar";
    return ret;
  }
  void deserialize(const QString &raw_data) override { m_value = raw_data; }
};

TEST_CASE("Test custom scalar by hand implementation") {
  auto a = CustomStringScalar();
  a.deserialize("initial");
  REQUIRE(a.to_qt() == "Decoration-initial");
  REQUIRE(a.GRAPHQL_NAME() == "CustomStringScalar");
  auto b = CustomStringScalar();
  b.deserialize("second");
  REQUIRE(a != b);
}
