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

} // namespace bases
} // namespace qtgql
