#pragma once
#include "testframework.hpp"
#include <QTest>

#include "qtgql/bases/bases.hpp"
#include "qtgql/gqltransportws/gqltransportws.hpp"
#include "testutils.hpp"

struct DebugHandler : public qtgql::bases::HandlerABC {
  qtgql::bases::GraphQLMessage m_message;
  explicit DebugHandler(const QString &query);

  QJsonArray m_errors;
  QJsonObject m_data;
  bool m_completed = false;
  void on_next(const QJsonObject &data) override;

  void on_error(const QJsonArray &errors) override;
  void on_completed() override;

  const qtgql::bases::GraphQLMessage &message() override { return m_message; }

  void wait_for_completed() const;
};

QString get_subscription_str(bool raiseOn5 = false,
                             const QString &op_name = "defaultOpName",
                             int target = 10);

bool count_eq_9(const QJsonObject &data);
