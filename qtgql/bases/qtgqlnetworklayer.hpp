#pragma once
#include <QJsonObject>
#include <QUuid>

namespace qtgql {
struct HashAbleABC {
  virtual QJsonObject serialize() const { throw "not implemented"; };
};

struct OperationMessage : public HashAbleABC {
  QUuid id;
  explicit OperationMessage() : id(QUuid::createUuid()) {}
};

// Replaces HandlerProto, To be extended by all consumers.
class GqlWsHandlerABC {
 public:
  virtual void onData(const QJsonObject &message) = 0;
  virtual void onError(const QJsonArray &errors) = 0;
  virtual void onCompleted() = 0;
  virtual const OperationMessage &message() = 0;
};

/*
class that should  support executing handlers
 and expected to call the handler's `on_data` /
`on_error` / 'on_completed' when the operation is completed.
*/
class QtGqlNetworkLayer {
 public:
  virtual void execute(std::shared_ptr<GqlWsHandlerABC> handler) {
    throw "not implemented";
  }
};
}  // namespace qtgql
