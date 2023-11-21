#include "utils.hpp"

DebugHandler::DebugHandler(const QString &query)
    : m_message{qtgql::bases::GraphQLMessage(query)} {};

void DebugHandler::on_next(const QJsonObject &data) {
  // here we copy the message though generally user wouldn't do this as it
  // would just use the reference to initialize some data
  m_data = data;
}

void DebugHandler::on_error(const QJsonArray &errors) { m_errors = errors; }

void DebugHandler::on_completed() { m_completed = true; }

void DebugHandler::wait_for_completed() const {
    qtgql_assert_m(QTest::qWaitFor([&]() -> bool { return m_completed; }, 1500),
                   "handler couldn't complete successfully.")} QString
    get_subscription_str(bool raiseOn5, const QString &op_name, int target) {
  QString ro5 = raiseOn5 ? "true" : "false";
  return QString("subscription %1 {count(target: %2, raiseOn5: %3) }")
      .arg(op_name, QString::number(target), ro5);
}
bool count_eq_9(const QJsonObject &data) {
  if (data.value("count").isDouble()) {
    auto ret = data.value("count").toInt();
    return ret == 9;
  }
  return false;
}
