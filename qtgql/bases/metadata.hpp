#pragma once
#include "QMap"
namespace qtgql {
namespace bases {

struct SelectionsConfig {
  // describes selections of a graphql operation.
  const QMap<QString, const SelectionsConfig *> selections;

  // for unions and fragments.
  const QMap<QString, const SelectionsConfig *> choices;
};

struct OperationMetadata {
  const QString operation_name;
  const SelectionsConfig selections;
};
}  // namespace bases
}  // namespace qtgql
