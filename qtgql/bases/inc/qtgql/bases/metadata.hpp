#pragma once
#include "../../../../../../../../MyConnandeps/Qt/6.5.0/gcc_64/include/QtCore/QMap"
namespace qtgql {

struct SelectionsConfig {
  // describes selections of a graphql operation.
  const QMap<QString, const SelectionsConfig*> selections;

  // for unions and fragments.
  const QMap<QString, const SelectionsConfig*> choices;
};

struct OperationMetadata {
  const QString operation_name;
  const SelectionsConfig selections;
};
}  // namespace qtgql
