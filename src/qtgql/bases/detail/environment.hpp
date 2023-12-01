#pragma once
#include "./networklayer.hpp"
#include "./objecttype.hpp"
#include "QMap"
#include "QString"
#include "objecttype.hpp"
#include "qtgql/qtgql_export.hpp"
#include <QTimer>
#include <QUuid>
#include <utility>

namespace qtgql::bases {
using namespace std::chrono_literals;

class QTGQL_EXPORT NodeInstanceStore {
  friend class EnvCache;

protected:
  std::map<QString, std::shared_ptr<NodeInterfaceABC>> m_nodes = {};

  [[nodiscard]] std::optional<std::shared_ptr<NodeInterfaceABC>>
  get_node(const scalars::Id &id) const;

  void add_node(const std::shared_ptr<NodeInterfaceABC> &node);

  void collect_garbage();
};

struct QTGQL_EXPORT EnvCacheOptions {
  std::chrono::milliseconds garbage_collection_period =
      std::chrono::milliseconds(30s);
};

class QTGQL_EXPORT EnvCache : public QObject {
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

class QTGQL_EXPORT Environment {
  typedef std::shared_ptr<Environment> SharedQtGqlEnv;
  //  using a ptr here since client is to be extended by implementors.
  typedef std::shared_ptr<NetworkLayerABC> SharedNetworkLayer;
  typedef std::unique_ptr<EnvCache> UniqueCache;

  SharedNetworkLayer m_network_layer;
  UniqueCache m_cache;
  static std::map<std::string, std::shared_ptr<Environment>> *ENV_MAP();
  std::string m_name;
  QUuid new_op_id;

public:
  // static members
  static void set_gql_env(const SharedQtGqlEnv &env);
  static std::optional<Environment::SharedQtGqlEnv>
  get_env(const std::string &name);
  static Environment::SharedQtGqlEnv get_env_strict(const std::string &name);
  // end static members

  Environment(const std::string &name, const SharedNetworkLayer &network_layer);

  Environment(std::string name, SharedNetworkLayer network_layer,
              UniqueCache cache_);

  void execute(const std::shared_ptr<HandlerABC> &handler);
  /*
   * You would generally not be needed for this method.
   * Though it might be of use for testing purposes.
   */
  [[nodiscard]] NetworkLayerABC *get_network_layer() const {
    if (!m_network_layer) {
      throw qtgql::exceptions::EnvironmentNotFoundError(
          "environment is not set up yet.");
    }
    return m_network_layer.get();
  };

  EnvCache *get_cache() { return m_cache.get(); }
};

} // namespace qtgql::bases
