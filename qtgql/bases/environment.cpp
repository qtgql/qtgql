#include "environment.hpp"
namespace qtgql {
namespace bases {

void Environment::set_gql_env(SharedQtGqlEnv env) {
  ENV_MAP[env->m_name] = env;
}

std::optional<Environment::SharedQtGqlEnv> Environment::get_gql_env(
    const QString &name) {
  if (!ENV_MAP.contains(name)) {
    return {};
  }
  return ENV_MAP.value(name);
}
};  // namespace bases
};  // namespace qtgql
