#include "qtgqlenvironment.hpp"

void qtgql::QtGqlEnvironment::set_gql_env(SharedQtGqlEnv env) {
  _ENV_MAP[env->m_name] = env;
}

qtgql::QtGqlEnvironment::SharedQtGqlEnv qtgql::QtGqlEnvironment::get_gql_env(
    const QString &name) {
  if (!_ENV_MAP.contains(name)) {
    throw "env name not found";
  }
  return _ENV_MAP.value(name);
}
