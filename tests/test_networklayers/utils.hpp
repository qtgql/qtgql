#pragma once
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "qtgql/bases/bases.hpp"
#include "qtgql/gqltransportws/gqltransportws.hpp"
#include "testutils.hpp"

struct DebugHandler : public bases::HandlerABC {
  bases::GraphQLMessage m_message;
  explicit DebugHandler(const QString &query)
      : m_message{bases::GraphQLMessage(query)} {};

  QJsonArray m_errors;
  QJsonObject m_data;
  bool m_completed = false;
  void on_next(const QJsonObject &data) override {
    // here we copy the message though generally user wouldn't do this as it
    // would just use the reference to initialize some data
    m_data = data;
  }

  void on_error(const QJsonArray &errors) override { m_errors = errors; }
  void on_completed() override { m_completed = true; }

  const bases::GraphQLMessage &message() override { return m_message; }

  inline void wait_for_completed() const {
    assert_m(QTest::qWaitFor([&]() -> bool { return m_completed; }, 1500),
             "handler couldn't complete successfully.")
  }
};

inline QString get_subscription_str(bool raiseOn5 = false,
                                    const QString &op_name = "defaultOpName",
                                    int target = 10) {
  QString ro5 = raiseOn5 ? "true" : "false";
  return QString("subscription %1 {count(target: %2, raiseOn5: %3) }")
      .arg(op_name, QString::number(target), ro5);
}

[[nodiscard]] bool count_eq_9(const QJsonObject &data) {
  if (data.value("count").isDouble()) {
    auto ret = data.value("count").toInt();
    return ret == 9;
  }
  return false;
}
