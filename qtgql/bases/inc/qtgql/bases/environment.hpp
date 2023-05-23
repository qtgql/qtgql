#pragma once
#include "../../../../../../../../MyConnandeps/Qt/6.5.0/gcc_64/include/QtCore/QMap"
#include "../../../../../../../../MyConnandeps/Qt/6.5.0/gcc_64/include/QtCore/QString"
#include "./networklayer.hpp"

namespace qtgql {

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
  typedef std::unique_ptr<NetworkLayer> UniqueNetworkLayer;

  UniqueNetworkLayer m_network_layer;
  inline static QMap<QString, SharedQtGqlEnv> _ENV_MAP = {};

 public:
  const QString m_name;
  explicit Environment(const QString &name, UniqueNetworkLayer network_layer)
      : m_name(name), m_network_layer(std::move(network_layer)){};

  void execute(const std::shared_ptr<HandlerABC> &handler) {
    m_network_layer->execute(handler);
  }
  static void set_gql_env(SharedQtGqlEnv env);
  static SharedQtGqlEnv get_gql_env(const QString &name);
};

}  // namespace qtgql
