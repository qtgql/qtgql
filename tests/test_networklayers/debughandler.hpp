#pragma once
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "qtgql/bases/bases.hpp"
#include "qtgql/gqlwstransport/gqlwstransport.hpp"
#include "testutils.hpp"

struct DebugHandler : public bases::HandlerABC {
  bases::GraphQLMessage m_message;
  explicit DebugHandler(const QString &query)
      : m_message{bases::GraphQLMessage(query)} {
    id = QUuid::createUuid();
  };

  QJsonArray m_errors;
  QJsonObject m_data;
  bool m_completed = false;
  [[nodiscard]] const QUuid &operation_id() const { return id; }
  void on_next(const QJsonObject &data) override {
    // here we copy the message though generally user wouldn't do this as it
    // would just use the reference to initialize some data
    m_data = data;
  }

  void on_error(const QJsonArray &errors) override { m_errors = errors; }
  void on_completed() override { m_completed = true; }

  const bases::GraphQLMessage &message() override { return m_message; }

  bool wait_for_completed() const {
    return QTest::qWaitFor([&]() -> bool { return m_completed; }, 1500);
  }
  // TODO: move this out of here.
  [[nodiscard]] bool count_eq_9() const {
    if (m_data.value("count").isDouble()) {
      auto ret = m_data.value("count").toInt();
      return ret == 9;
    }
    return false;
  }
};
