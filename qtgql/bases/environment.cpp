#include "environment.hpp"
namespace qtgql {
namespace bases {

void Environment::set_gql_env(SharedQtGqlEnv env) {
  _ENV_MAP[env->m_name] = env;
}

std::optional<Environment::SharedQtGqlEnv> Environment::get_gql_env(
    const QString &name) {
  if (!_ENV_MAP.contains(name)) {
    return {};
  }
  return _ENV_MAP.value(name);
}
};  // namespace bases
};  // namespace qtgql
