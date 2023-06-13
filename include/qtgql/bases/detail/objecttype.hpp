#pragma once
#include <type_traits>

#include "QDebug"
#include "QObject"
#include "QSet"
#include "metadata.hpp"

namespace qtgql {
namespace bases {

class ObjectTypeABC : public QObject {
  Q_OBJECT

  Q_PROPERTY(QString __typeName READ getTypeName CONSTANT)

private:
  inline const QString getTypeName() const { return "__NOT_IMPLEMENTED__"; }

public:
  using QObject::QObject;
};


class NodeInterfaceABC : public ObjectTypeABC {
public:
  using ObjectTypeABC::ObjectTypeABC;

  virtual const QString &get_id() const = 0;

  // updates a node based on new GraphQL data.
  virtual void update(const QJsonObject &data,
                      const SelectionsConfig &selections, const OperationMetadata &metadata) = 0;

};

// Should be used by Node interface jinja implementation ONLY!
template <typename T>
concept extendsNodeInterfaceABC =
    std::is_base_of<NodeInterfaceABC, T>::value;


template <extendsNodeInterfaceABC T> class NodeInstanceStore {
  typedef std::shared_ptr<T> T_sharedQObject;

protected:
  std::map<QString, UniqueRecord> m_records;

public:
  std::optional<T_sharedQObject> get_node(const QString &id) const {
    if (m_records.contains(id)) {
      return {m_records.at(id)->node};
    }
    return {};
  }

  void add_node(T_sharedQObject node, const QUuid &operation_id) {
    if (node.get()) {
      auto record = std::make_unique<qtgql::bases::NodeRecord<T>>(node);
      record->retain(operation_id);
      m_records[node->get_id()] = std::move(record);
    }
  };

  void loose(const QString &node_id, const QUuid &operation_id) {
    m_records.at(node_id)->loose(operation_id);
    if (!m_records.at(node_id)->has_retainers()) {
      m_records.erase(node_id);
    }
  }
};

} // namespace bases
} // namespace qtgql
