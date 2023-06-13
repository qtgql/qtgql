#pragma once
#include <QMap>
#include <QUuid>
#include <utility>

namespace qtgql {
namespace bases {

struct SelectionsConfig {
  // describes selections of a graphql operation.
  typedef QMap<QString, SelectionsConfig> SelectionsMap;
  SelectionsMap selections = SelectionsMap();

  // for unions and fragments.
  SelectionsMap choices = SelectionsMap();
};

struct OperationMetadata {
  const QUuid operation_id;
  OperationMetadata(const QUuid& id): operation_id(id){}
    OperationMetadata() = delete;
};
} // namespace bases
} // namespace qtgql
