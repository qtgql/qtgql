#include "testframework.hpp"
#include <QString>
#include <QTest>

#include "qtgql/customscalars/customscalars.hpp"

class CustomStringScalar
    : public qtgql::customscalars::CustomScalarABC<QString, QString> {
  QString m_cached;

public:
  using qtgql::customscalars::CustomScalarABC<QString,
                                              QString>::CustomScalarABC;

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

  void deserialize(const QJsonValue &raw_data) override {
    m_value = raw_data.toString();
  }
  [[nodiscard]] QJsonValue serialize() const override { return {m_value}; }
};

void preform_test(CustomStringScalar &s) {
  REQUIRE(s.to_qt() == "Decoration-initial");
  REQUIRE(s.GRAPHQL_NAME() == "CustomStringScalar");
  auto b = CustomStringScalar();
  b.deserialize("second");
  REQUIRE(s != b);
}

TEST_CASE("Test custom scalar by hand implementation") {
  SECTION("from json") {
    auto cs = CustomStringScalar();
    cs.deserialize({"initial"});
    preform_test(cs);
  }
  SECTION("to_json") {
    auto s = CustomStringScalar("initial");
    preform_test(s);
  }
}
