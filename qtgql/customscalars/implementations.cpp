#include "implementations.hpp"
namespace qtgql {
namespace customscalars {
const QString &DateTimeScalar::to_qt() {
  if (m_should_update) {
    m_cached_to_qt = m_value.toString("hh:mm (dd.mm.yyyy)");
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

void DateScalar::deserialize(const QJsonValue &raw_data) {
  m_value = QDate::fromString(raw_data.toString(), Qt::DateFormat(Qt::ISODate));
  m_should_update = true;
}

const QString &DateScalar::GRAPHQL_NAME() {
  static const QString ret = "Date";
  return ret;
}

const QString &DateScalar::to_qt() {
  if (m_should_update) {
    m_cached_to_qt = m_value.toString("dd.MM.yyyy");
    m_should_update = false;
  }
  return m_cached_to_qt;
}

void TimeScalar::deserialize(const QJsonValue &raw_data) {
  m_value = QTime::fromString(raw_data.toString(), Qt::DateFormat(Qt::ISODate));
  m_should_update = true;
}

const QString &TimeScalar::GRAPHQL_NAME() {
  static const QString ret = "Time";
  return ret;
}

const QString &TimeScalar::to_qt() {
  if (m_should_update) {
    m_cached_to_qt = m_value.toString();
    m_should_update = false;
  }
  return m_cached_to_qt;
}

void DecimalScalar::deserialize(const QJsonValue &raw_data) {
  m_value = raw_data.toString();
}

const QString &DecimalScalar::GRAPHQL_NAME() {
  static const QString ret = "Decimal";
  return ret;
}

const QString &DecimalScalar::to_qt() { return m_value; }
};  // namespace customscalars
};  // namespace qtgql
