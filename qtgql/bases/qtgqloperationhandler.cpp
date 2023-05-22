#include "qtgqloperationhandler.hpp"

namespace qtgql {

void _QtGqlOperationHandlerABCSignals::set_completed(bool v) {
  if (m_completed != v) {
    m_completed = v;
    emit completedChanged();
  }
  if (m_completed) {
    set_operation_on_flight(false);
  }
}
void _QtGqlOperationHandlerABCSignals::set_operation_on_flight(bool v) {
  if (m_operation_on_the_fly != v) {
    m_operation_on_the_fly = v;
    emit operationOnFlightChanged();
  }
}

bool _QtGqlOperationHandlerABCSignals::completed() { return m_completed; }

bool _QtGqlOperationHandlerABCSignals::operation_on_flight() {
  return m_operation_on_the_fly;
}

}  // namespace qtgql
