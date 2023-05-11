#pragma once
#include <QObject>

#include "qtgqlenvironment.hpp"
#include "qtgqlmetadata.hpp"

namespace qtgql {

class _QtGqlOperationHandlerBaseSignals : public QObject {
  Q_OBJECT

 signals:
  void dataChanged();
  void completedChanged();
  void operationOnFlightChanged();
  void error(const QJsonObject &);
};

class QtGqlOperationHandlerBase : public _QtGqlOperationHandlerBaseSignals,
                                  QtGqlHandlerABC {
 protected:
  bool _completed = false;
  bool _operation_on_the_fly = false;
  // abstract functions.
  virtual const QString &ENV_NAME() = 0;
  virtual const qtgql::OperationMetadata &OPERATION_METADATA() = 0;
  // end abstract functions.

  const auto &environment() {
    static auto m_env = qtgql::QtGqlEnvironment::get_gql_env(ENV_NAME());
    return m_env;
  }

  void fetch() {
    if (!_operation_on_the_fly && !_completed) {
      set_operation_on_flight(true);
      environment()->
    }
  };
};
};  // namespace qtgql
