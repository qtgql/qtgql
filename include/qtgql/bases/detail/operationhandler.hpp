#pragma once
#include "environment.hpp"
#include <QObject>

namespace qtgql::bases {

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

  void set_completed(bool v) {
    if (m_completed != v) {
      m_completed = v;
      emit completedChanged();
    }
    if (m_completed) {
      set_operation_on_flight(false);
    }
  }

  void set_operation_on_flight(bool v) {
    if (m_operation_on_the_fly != v) {
      m_operation_on_the_fly = v;
      emit operationOnFlightChanged();
    }
  }

public:
  using QObject::QObject;

  [[nodiscard]] inline bool completed() const { return m_completed; };

  [[nodiscard]] inline bool operation_on_flight() const {
    return m_operation_on_the_fly;
  }
};

// Must be extended in the templates.
class OperationHandlerABC
    : public _OperationHandlerABCSignals,
      public bases::HandlerABC,
      public std::enable_shared_from_this<OperationHandlerABC> {
protected:
  GraphQLMessage m_message_template;

  const std::shared_ptr<Environment> &environment() {
    static auto m_env = Environment::get_env(ENV_NAME());
    return m_env.value();
  };

public:
  explicit OperationHandlerABC(GraphQLMessage message)
      : _OperationHandlerABCSignals(), m_message_template(std::move(message)) {
    id = QUuid::createUuid();
  }

  QJsonObject variables() const {
    if (m_message_template.variables.has_value())
      return m_message_template.variables.value();
    else {
      return {};
    }
  }
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
  void set_variables(const QJsonObject &vars) {
    m_message_template.set_variables(vars);
  }

  const bases::GraphQLMessage &message() override {
    return m_message_template;
  };

  void on_completed() override { set_completed(true); };

  void on_error(const QJsonArray &errors) override {
    set_completed(true);
    emit error(errors);
  };
};
}; // namespace qtgql::bases
