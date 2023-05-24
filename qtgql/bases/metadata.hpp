#pragma once
#include <utility>

#include "QMap"
namespace qtgql {
namespace bases {
struct SelectionConfig;

struct SelectionsConfig {
  // describes selections of a graphql operation.
  typedef QMap<QString, const SelectionConfig *> SelectionsMap;
  const SelectionsMap selections;

  // for unions and fragments.
  const SelectionsMap choices;
  explicit SelectionsConfig(SelectionsMap selections = {},
                            SelectionsMap choices_ = {})
      : selections(std::move(selections)), choices(std::move(choices_)){};
};

struct OperationMetadata {
  const QString operation_name;
  const SelectionsConfig selections;
};
}  // namespace bases
}  // namespace qtgql
