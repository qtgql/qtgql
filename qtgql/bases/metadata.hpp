#pragma once
#include <utility>

#include "QMap"
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
  const QString operation_name;
  SelectionsConfig selections;
};
}  // namespace bases
}  // namespace qtgql
