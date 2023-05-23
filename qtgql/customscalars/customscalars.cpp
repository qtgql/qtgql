#include "inc/qtgql/customscalars/customscalars.hpp"

namespace qtgql {

const QString &DateTimeScalar::to_qt() {
  if (m_should_update) {
    m_cached_to_qt = m_value.toString("hh:mm (dd.mm.yy)");
    m_should_update = false;
  }
  return m_cached_to_qt;
}

const QString &DateTimeScalar::GRAPHQL_NAME() {
  static const QString ret = "DateTime";
  return ret;
}

void DateTimeScalar::deserialize(const QJsonValue &raw_data) {
  m_value =
      QDateTime::fromString(raw_data.toString(), Qt::DateFormat(Qt::ISODate));
  m_should_update = true;
}

void DecimalScalar::deserialize(const QJsonValue &raw_data) {
  m_value = raw_data.toString();
}

const QString &DecimalScalar::GRAPHQL_NAME() {
  static const QString ret = "Decimal";
  return ret;
}

const QString &DecimalScalar::to_qt() { return m_value; }
}  // namespace qtgql
