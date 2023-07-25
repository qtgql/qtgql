#include "qtgql/bases/bases.hpp"
#include <QUuid>
#include <algorithm>

namespace qtgql::gqlwstransport {
namespace ranges = std::ranges;

class OperationHandlerContainer {
  typedef std::pair<QUuid, std::shared_ptr<bases::OperationHandlerABC>>
      UuidHandlerPair;
  std::list<UuidHandlerPair> m_handlers;

public:
  bool contains(const QUuid &operation_id) {
    auto uuid_eq = [&](const UuidHandlerPair &other) -> bool {
      return operation_id == other.first;
    };

#if __cplusplus > 201703L
    return ranges::any_of(m_handlers, uuid_eq);
#else
    for (const auto &uuid_handler_pair : m_handlers) {
      if (uuid_eq(uuid_handler_pair))
        return true;
    }
    return false;
#endif
  }
  std::optional<std::shared_ptr<bases::OperationHandlerABC>>
  get_handler(const QUuid &op_id) {
    for (const auto &uuid_handler_pair : m_handlers) {
      if (uuid_handler_pair.first == op_id)
        return uuid_handler_pair.second;
    }
    return {};
  }
  /* inserts a handler only if the operation_id was not inserted already.
   returns true if successfully inserted.
   */
  bool safe_insert(const UuidHandlerPair &uuid_handler_pair) {
    if (!contains(uuid_handler_pair.first)) {
      m_handlers.push_front(uuid_handler_pair);
      return true;
    }
    return false;
  }

  void remove(const QUuid &op_id) {
    for (const auto &uuid_handler_pair : m_handlers) {
      if (uuid_handler_pair.first == op_id)
        m_handlers.remove(uuid_handler_pair);
    }
  }
};
} // namespace qtgql::gqlwstransport
