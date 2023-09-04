#pragma once
#include <QTimer>
#include <utility>

#include "./networklayer.hpp"
#include "./objecttype.hpp"
#include "QMap"
#include "QString"
#include "objecttype.hpp"

namespace qtgql::bases {
using namespace std::chrono_literals;

class NodeInstanceStore {
  friend class EnvCache;

protected:
  std::map<QString, std::shared_ptr<NodeInterfaceABC>> m_nodes = {};

  [[nodiscard]] std::optional<std::shared_ptr<NodeInterfaceABC>>
  get_node(const scalars::Id &id) const;

  void add_node(const std::shared_ptr<NodeInterfaceABC> &node);

  void collect_garbage();
};

struct EnvCacheOptions {
  std::chrono::milliseconds garbage_collection_period =
      std::chrono::milliseconds(30s);
};

class EnvCache : public QObject {
  Q_OBJECT
protected:
  NodeInstanceStore m_store = {};
  QTimer *m_gc_timer;

public:
  explicit EnvCache(const EnvCacheOptions &options = EnvCacheOptions());

  [[nodiscard]] auto get_node(const scalars::Id &id) const {
    return m_store.get_node(id);
  }
  auto add_node(const std::shared_ptr<NodeInterfaceABC> &node) {
    return m_store.add_node(node);
  }
  auto collect_garbage() { m_store.collect_garbage(); }
};

struct EnvironmentOptions {};

/*Encapsulates a schema interaction.

The schema **must** be coherent with the schema use by the code
generator. This class is used by the codegen and not to be
instantiated directly.

:member client: The network layer for communicated the GraphQL server,
all the generated handlers for this environment  would use this layer.

:member name: This would be used to retrieve this environment from the env map
by the generated handlers based on the configurations.
*/

class Environment {
  typedef std::shared_ptr<Environment> SharedQtGqlEnv;
  //  using a ptr here since client is to be extended by implementors.
  typedef std::unique_ptr<NetworkLayerABC> UniqueNetworkLayer;
  typedef std::unique_ptr<EnvCache> UniqueCache;

  UniqueNetworkLayer m_network_layer;
  UniqueCache m_cache =
      std::make_unique<EnvCache>(); // using unique pointers for extendability
  static std::map<std::string, std::shared_ptr<Environment>> *ENV_MAP();

public:
  // static members
  static void set_gql_env(const SharedQtGqlEnv &env);
  static std::optional<Environment::SharedQtGqlEnv>
  get_env(const std::string &name);
  static Environment::SharedQtGqlEnv get_env_strict(const std::string &name);
  // end static members

  const std::string m_name;

  Environment(std::string name, UniqueNetworkLayer network_layer)
      : m_name(std::move(name)), m_network_layer(std::move(network_layer)){};

  Environment(std::string name, UniqueNetworkLayer network_layer,
              UniqueCache cache_)
      : m_name(std::move(name)), m_network_layer(std::move(network_layer)),
        m_cache(std::move(cache_)){};

  void execute(const std::shared_ptr<HandlerABC> &handler) {
    m_network_layer->execute(handler);
  }
  /*
   * You would generally not be needed for this method.
   * Though it might be of use for testing purposes.
   */
  [[nodiscard]] NetworkLayerABC *get_network_layer() const {
    return m_network_layer.get();
  };

  EnvCache *get_cache() { return m_cache.get(); }
};

} // namespace qtgql::bases
