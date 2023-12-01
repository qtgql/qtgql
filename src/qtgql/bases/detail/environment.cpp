#include "environment.hpp"

using namespace qtgql::bases;

void NodeInstanceStore::add_node(
    const std::shared_ptr<qtgql::bases::NodeInterfaceABC> &node) {
  if (node.get()) {
    m_nodes.emplace(*node->get_id(), node);
  }
}

std::optional<std::shared_ptr<qtgql::bases::NodeInterfaceABC>>
NodeInstanceStore::get_node(const scalars::Id &id) const {
  if (m_nodes.contains(id)) {
    return {m_nodes.at(id)};
  }
  return {};
}

void NodeInstanceStore::collect_garbage() {
  // adopted, shamelessly, from https://stackoverflow.com/a/8234813/16776498
  for (auto it = m_nodes.begin(); it != m_nodes.end() /* not hoisted */;
       /* no increment */)
    if (it->second.use_count() == 1) {
      it = m_nodes.erase(it);
    } else {
      ++it;
    }
}

void Environment::set_gql_env(const SharedQtGqlEnv &env) {
  ENV_MAP()->emplace(env->m_name, env);
}

std::map<std::string, std::shared_ptr<Environment>> *Environment::ENV_MAP() {
  static std::map<std::string, std::shared_ptr<Environment>> map;
  return &map;
}

std::optional<Environment::SharedQtGqlEnv>
Environment::get_env(const std::string &name) {
  if (!ENV_MAP()->contains(name)) {
    return {};
  }
  return ENV_MAP()->at(name);
}

Environment::SharedQtGqlEnv
Environment::get_env_strict(const std::string &name) {
  if (ENV_MAP()->contains(name)) {
    return ENV_MAP()->at(name);
  }
  throw exceptions::EnvironmentNotFoundError(name);
}

Environment::Environment(const std::string &name,
                         const Environment::SharedNetworkLayer &network_layer) {
  m_name = name;
  m_network_layer = network_layer;
  m_cache = std::make_unique<EnvCache>();
}

Environment::Environment(std::string name,
                         Environment::SharedNetworkLayer network_layer,
                         Environment::UniqueCache cache_)
    : m_name(std::move(name)), m_network_layer(std::move(network_layer)),
      m_cache(std::move(cache_)) {}

void Environment::execute(const std::shared_ptr<HandlerABC> &handler) {
  new_op_id = QUuid::createUuid();
  m_network_layer->execute(handler, new_op_id);
}

EnvCache::EnvCache(const qtgql::bases::EnvCacheOptions &options)
    : QObject(nullptr) {
  m_gc_timer = new QTimer(this);
  m_gc_timer->setInterval(options.garbage_collection_period);
  connect(m_gc_timer, &QTimer::timeout, this, &EnvCache::collect_garbage);
  m_gc_timer->start();
}
