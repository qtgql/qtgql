#include "inc/qtgql/customscalars/customscalars.hpp"

namespace qtgql {

const QString &DateTimeScalar::to_qt() {
  static const QString format_string = "%H:%M (%m/%d/%Y)";
  if (m_should_update) {
    m_cached_to_qt = m_value.toString(format_string);
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

}  // namespace qtgql
