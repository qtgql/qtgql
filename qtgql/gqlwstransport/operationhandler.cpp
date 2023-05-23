#include "qtgql/gqlwstransport/operationhandler.hpp"

namespace qtgql {

void _OperationHandlerABCSignals::set_completed(bool v) {
  if (m_completed != v) {
    m_completed = v;
    emit completedChanged();
  }
  if (m_completed) {
    set_operation_on_flight(false);
  }
}
void _OperationHandlerABCSignals::set_operation_on_flight(bool v) {
  if (m_operation_on_the_fly != v) {
    m_operation_on_the_fly = v;
    emit operationOnFlightChanged();
  }
}

bool _OperationHandlerABCSignals::completed() { return m_completed; }

bool _OperationHandlerABCSignals::operation_on_flight() {
  return m_operation_on_the_fly;
}

}  // namespace qtgql
