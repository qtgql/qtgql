#pragma once
#include <QObject>

#include "../gqlwstransport/gqlwstransport.hpp"
#include "qtgqlenvironment.hpp"
#include "qtgqlmetadata.hpp"

namespace qtgql {

class _QtGqlOperationHandlerABCSignals : public QObject {
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
  void error(const QJsonArray &);

 protected slots:
  void set_completed(bool v);
  void set_operation_on_flight(bool v);

 public:
  using QObject::QObject;
};

// NOTE: This class should not be defined in the .cpp since it is abstract.
class QtGqlOperationHandlerABC
    : public QtGqlHandlerABC,
      public _QtGqlOperationHandlerABCSignals,
      public std::enable_shared_from_this<QtGqlOperationHandlerABC> {
 protected:
  const std::shared_ptr<QtGqlEnvironment> &environment() {
    static auto m_env = QtGqlEnvironment::get_gql_env(ENV_NAME());
    return m_env;
  };
  QJsonObject m_variables;
  GqlWsTrnsMsgWithID m_message_template;

 public:
  //    this should be protected since it should only be constructed with a
  //    shared ptr
  QtGqlOperationHandlerABC()
      : _QtGqlOperationHandlerABCSignals::_QtGqlOperationHandlerABCSignals(),
        m_message_template({}) {}

  // abstract functions.
  virtual const QString &ENV_NAME() = 0;
  // end abstract functions.

  void fetch() {
    if (!m_operation_on_the_fly && !m_completed) {
      set_operation_on_flight(true);
      auto a = shared_from_this();
      Q_ASSERT_X(a, "QtGqlOperationHandlerABC",
                 "Could not get a shared_ptr from `this` make sure to only "
                 "instantiate this with `std::make_shared`");
      environment()->execute(a);
    }
  }
  void refetch() {
    set_completed(false);
    fetch();
  };
  const HashAbleABC &message() override {
    m_message_template.set_variables(m_variables);
    return m_message_template;
  };
  void on_completed() override { set_completed(true); };
  void on_error(const QJsonArray &errors) override {
    set_completed(true);
    emit error(errors);
  };
};
};  // namespace qtgql
