#pragma once
#include <qtgql/customscalars/customscalars.hpp>

class CountryScalar
    : public qtgql::customscalars::CustomScalarABC<std::string, QString> {

  static const std::map<std::string, std::string> &countries_map() {
    static std::map<std::string, std::string> ret = {{"isr", "Israel"},
                                                     {"uk", "United Kingdom"}};
    return ret;
  }

public:
  const QString &GRAPHQL_NAME() final {
    static QString ret("Country");
    return ret;
  };
  void deserialize(const QJsonValue &raw_data) final {
    m_value = raw_data.toString().toStdString();
    m_qt_value_cached = QString::fromStdString(countries_map().at(m_value));
  }
  const QString &to_qt() final { return m_qt_value_cached; };
  [[nodiscard]] QJsonValue serialize() const final {
    return {QString::fromStdString(m_value)};
  }
};
