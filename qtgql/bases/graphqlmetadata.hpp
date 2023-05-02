#pragma once
#include <QMap>

struct SelectionsConfig {
  // describes selections of a graphql operation.
  const QMap<QString, std::optional<SelectionsConfig>> selections;

  // for unions and fragments.
  const QMap<QString, SelectionsConfig> choices;
};

struct OperationMetadata {
  const QString operation_name;
  const SelectionsConfig selections;
};
