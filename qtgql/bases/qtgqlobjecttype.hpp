#pragma once
#include <QDebug>
#include <QObject>
#include <QSet>
#include <type_traits>

#include "qtgqlmetadata.hpp"

namespace qtgql {

class QtGqlObjectTypeABC : public QObject {
  Q_OBJECT
  Q_PROPERTY(QString typeName READ getTypeName CONSTANT)

 private:
  inline const QString getTypeName() const { return  "__NOT_IMPLEMENTED__"; }

 public:
  using QObject::QObject;
};

class QtGqlObjectTypeABCWithID : public QtGqlObjectTypeABC {
 public:
  using QtGqlObjectTypeABC::QtGqlObjectTypeABC;
  virtual const QString &get_id() const = 0;

  // TODO: can't use constructor for this class since it is abstract.
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
concept extendsQtGqlObjectTypeABCWithID =
    std::is_base_of<QtGqlObjectTypeABCWithID, T>::value;

// stores global node of graphql type and it's retainers.
template <extendsQtGqlObjectTypeABCWithID T>
class NodeRecord {
  QSet<QString> m_retainers;
  typedef std::shared_ptr<T> T_sharedQObject;

 public:
  T_sharedQObject node;
  NodeRecord() { throw "tried to instantiate without arguments"; };
  NodeRecord(const T_sharedQObject &node_) { node = node_; };

  void retain(const QString &operation_name) {
    m_retainers.insert(operation_name);
  }
  void loose(const QString &operation_name) {
    m_retainers.remove(operation_name);
  }
  bool has_retainers() const { return m_retainers.isEmpty(); }
};

template <extendsQtGqlObjectTypeABCWithID T>
class QGraphQLObjectStore {
  typedef std::shared_ptr<NodeRecord<T>> T_sharedRecord;

 protected:
  QMap<QString, T_sharedRecord> m_data;

 public:
  std::optional<T_sharedRecord> get_record(const QString &id) const {
    if (m_data.contains(id)) {
      return {m_data.value(id)};
    }
    return {};
  }

  void add_record(const T_sharedRecord &record) {
    if (record) {
      auto node = record->node;
      if (node) {
        m_data.insert(node->get_id(), record);
      }
    }
  };

  void loose(const std::shared_ptr<T> &node, const QString &operation_name) {
    auto record = m_data.value(node->get_id());
    record->loose(operation_name);
    if (!record->has_retainers()) {
      m_data.remove(node->get_id());
      qDebug() << "Node with ID: " << node->get_id() << "has ref count of "
               << node.use_count();
    }
  }
};

}  // namespace qtgql
