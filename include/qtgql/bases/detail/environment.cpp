#include "environment.hpp"



namespace qtgql {
namespace bases {
    void NodeInstanceStore::add_node(const std::shared_ptr <qtgql::bases::NodeInterfaceABC> &node) {
        if (node.get()) {
            m_nodes.emplace(node->get_id(), node);
        }
    }

    std::optional <std::shared_ptr<qtgql::bases::NodeInterfaceABC>> NodeInstanceStore::get_node(const scalars::Id &id) const {
        if (m_nodes.contains(id)) {
            return {m_nodes.at(id)};
        }
        return {};
    }

    void NodeInstanceStore::collect_garbage() {
        // adopted, shamelessly, from https://stackoverflow.com/a/8234813/16776498
        for (auto it = m_nodes.begin(); it != m_nodes.end() /* not hoisted */; /* no increment */)
            if(it->second.use_count() == 1){
                it = m_nodes.erase(it);
            }
            else
            {
                ++it;
            }

    }

    void Environment::set_gql_env(SharedQtGqlEnv env) {
  ENV_MAP[env->m_name] = env;
}

std::optional<Environment::SharedQtGqlEnv>
Environment::get_env(const QString &name) {
  if (!ENV_MAP.contains(name)) {
    return {};
  }
  return ENV_MAP.value(name);
}

    Environment::SharedQtGqlEnv Environment::get_env_strict(const QString &name) {
        if (ENV_MAP.contains(name)) {
            return ENV_MAP.value(name);
        }
        throw exceptions::EnvironmentNotFoundError(name.toStdString());
    }
}; // namespace bases
}; // namespace qtgql
