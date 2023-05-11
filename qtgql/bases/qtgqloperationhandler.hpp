#pragma once
#include <QObject>

#include "qtgqlenvironment.hpp"
#include "qtgqlmetadata.hpp"

namespace qtgql {

class _QtGqlOperationHandlerBaseSignals : public QObject {
  Q_OBJECT
  Q_PROPERTY(bool completed MEMBER m_completed NOTIFY completedChanged)
  Q_PROPERTY(
      bool operationOnFlight MEMBER m_completed NOTIFY operationOnFlightChanged)

 protected:
  bool m_completed = false;
  bool m_operation_on_the_fly = false;

 signals:
  void completedChanged();
  void operationOnFlightChanged();
  void error(const QJsonObject &);

 protected slots:
  void set_completed(bool v);
  void set_operation_on_flight(bool v);

 public:
  using QObject::QObject;
};

// NOTE: This class should not be defined in the .cpp since it is abstract.
class QtGqlOperationHandlerBase
    : public QtGqlHandlerABC,
      public _QtGqlOperationHandlerBaseSignals,
      protected std::enable_shared_from_this<QtGqlOperationHandlerBase> {
 protected:
  const std::shared_ptr<QtGqlEnvironment> &environment() {
    static auto m_env = QtGqlEnvironment::get_gql_env(ENV_NAME());
    return m_env;
  };

 public:
  //    this should be protected since it should only be constructed with a
  //    shared ptr
  QtGqlOperationHandlerBase()
      : _QtGqlOperationHandlerBaseSignals::_QtGqlOperationHandlerBaseSignals() {
  }

  // abstract functions.
  virtual const QString &ENV_NAME() = 0;
  virtual const OperationMetadata &OPERATION_METADATA() = 0;
  // end abstract functions.
  void fetch() {
    if (!m_operation_on_the_fly && !m_completed) {
      set_operation_on_flight(true);
      auto a = shared_from_this();
      Q_ASSERT_X(a, "QtGqlOperationHandlerBase",
                 "Could not get a shared_ptr from `this` make sure to only "
                 "instantiate this with `std::make_shared`");
      environment()->execute(a);
    }
  }
  void refetch() {
    set_completed(false);
    fetch();
  };
};
};  // namespace qtgql
