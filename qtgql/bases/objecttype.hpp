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

  Q_PROPERTY(QString typeName READ getTypeName CONSTANT)

private:
  inline const QString getTypeName() const { return "__NOT_IMPLEMENTED__"; }

public:
  using QObject::QObject;
};

class ObjectTypeABCWithID : public ObjectTypeABC {
public:
  using ObjectTypeABC::ObjectTypeABC;

  virtual const QString &get_id() const = 0;

  // updates a node based on new GraphQL data.
  virtual void update(const QJsonObject &data,
                      const SelectionsConfig &selections) = 0;

  /*
  releases all child objects if exists.

  note that this method would be useful only if the object
  (or one of its children) has an id and a reference in the store,
  otherwise the pointer to this object is release and this object
  would be deleted.
  */
  virtual void loose(const OperationMetadata &metadata) = 0;
};

template <typename T>
concept extendsObjectTypeABCWithID =
    std::is_base_of<ObjectTypeABCWithID, T>::value;

// stores global node of graphql type and it's retainers.
template <extendsObjectTypeABCWithID T> class NodeRecord {
  QSet<QUuid> m_retainers;
  typedef std::shared_ptr<T> T_sharedQObject;

public:
  T_sharedQObject node;

  NodeRecord() { throw "tried to instantiate without arguments"; };

  explicit NodeRecord(const T_sharedQObject &node_) { node = node_; };

  void retain(const QUuid &operation_id) { m_retainers.insert(operation_id); }

  void loose(const QUuid &operation_id) {
    qDebug() << "removing: " << operation_id << "from: " << m_retainers;
    m_retainers.remove(operation_id);
  }

  [[nodiscard]] bool has_retainers() const { return !m_retainers.isEmpty(); }
};

template <extendsObjectTypeABCWithID T> class ObjectStore {
  typedef std::shared_ptr<T> T_sharedQObject;
  typedef std::unique_ptr<NodeRecord<T>> UniqueRecord;

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
