/*
 * Encapsulates the API which will be used by the codegen
 * currently the only implementation is with graphql-ws-transport protocol
 * at ../gqlwstransport dir.
 */
#pragma once
#include "../../../../../../../../MyConnandeps/Qt/6.5.0/gcc_64/include/QtCore/QJsonObject"
#include "../../../../../../../../MyConnandeps/Qt/6.5.0/gcc_64/include/QtCore/QUuid"
#include "../../../../utils/utils.hpp"
namespace qtgql {
struct HashAbleABC {
  [[nodiscard]] virtual QJsonObject serialize() const {
    throw NotImplementedError({});
  };
};

// To be extended by all consumers (Replaced `HandlerProto` in Python).
struct HandlerABC {
  [[nodiscard]] virtual const QUuid &operation_id() const = 0;
  // https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md#next
  virtual void on_next(const QJsonObject &message) = 0;
  // https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md#error
  virtual void on_error(const QJsonArray &errors) = 0;
  // https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md#complete
  virtual void on_completed() = 0;
  virtual const HashAbleABC &message() = 0;
};

/*
class that should  support executing handlers
 and expected to call the handler's `on_data` /
`on_error` / 'on_completed' when the operation is completed.
*/
class NetworkLayer {
 public:
  virtual void execute(const std::shared_ptr<HandlerABC> &handler) {
    throw NotImplementedError({});
  }
};
}  // namespace qtgql
