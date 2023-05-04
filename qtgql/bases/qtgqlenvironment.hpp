#pragma once
#include <QMap>
#include <QString>

#include "./qtgqlnetworklayer.hpp"

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

class QtGqlEnvironment {
  typedef std::shared_ptr<QtGqlEnvironment> SharedQtGqlEnv;
  typedef std::unique_ptr<QtGqlNetworkLayer> UniqueNetworkLayer;

  const UniqueNetworkLayer m_network_layer;
  inline static QMap<QString, SharedQtGqlEnv> _ENV_MAP = {};

 public:
  const QString m_name;
  explicit QtGqlEnvironment(const QString &name,
                            UniqueNetworkLayer network_layer)
      : m_name(name), m_network_layer(std::move(network_layer)){};

  static void set_gql_env(SharedQtGqlEnv env);
  static SharedQtGqlEnv get_gql_env(const QString &name);
};

}  // namespace qtgql
