#pragma once
#include <QObject>

#include "gqlwstransport.hpp"
#include "qtgql/bases/bases.hpp"

namespace qtgql {
namespace gqlwstransport {

class _OperationHandlerABCSignals : public QObject {
  Q_OBJECT

  Q_PROPERTY(bool completed READ completed NOTIFY completedChanged)
  Q_PROPERTY(bool operationOnFlight READ operation_on_flight NOTIFY
                 operationOnFlightChanged)

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

  bool completed() const;

  bool operation_on_flight();
};

// NOTE: This class should not be defined in the .cpp since it is abstract.
class OperationHandlerABC
    : public bases::HandlerABC,
      public _OperationHandlerABCSignals,
      public std::enable_shared_from_this<OperationHandlerABC> {
 protected:
  const std::shared_ptr<bases::Environment> &environment() {
    static auto m_env = bases::Environment::get_gql_env(ENV_NAME());
    return m_env;
  };
  QJsonObject m_variables;
  GqlWsTrnsMsgWithID m_message_template = GqlWsTrnsMsgWithID{{}};

 public:
  explicit OperationHandlerABC(GqlWsTrnsMsgWithID message)
      : _OperationHandlerABCSignals(), m_message_template(std::move(message)) {}

  // abstract functions.
  virtual const QString &ENV_NAME() = 0;
  virtual const bases::OperationMetadata &OPERATION_METADATA() = 0;
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

  const bases::HashAbleABC &message() override {
    m_message_template.set_variables(m_variables);
    return m_message_template;
  };

  void on_completed() override { set_completed(true); };

  void on_error(const QJsonArray &errors) override {
    set_completed(true);
    emit error(errors);
  };
};
};  // namespace gqlwstransport
}  // namespace qtgql
