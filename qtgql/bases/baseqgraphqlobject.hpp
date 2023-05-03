#pragma once

#include <QDebug>
#include <QObject>
#include <QSet>

#include "graphqlmetadata.hpp"

namespace qtgql {

class BaseQGraphQLObject : public QObject {
  Q_OBJECT
  Q_PROPERTY(QString typeName READ getTypeName CONSTANT)

 private:
  const QString getTypeName() const { return TYPE_NAME; }

 public:
  inline static const QString TYPE_NAME = "__NOT_IMPLEMENTED__";
  explicit BaseQGraphQLObject(QObject *parent = nullptr);

  template <typename T>
  static std::shared_ptr<T> from_dict(QObject *parent, const QJsonObject &data,
                                      const SelectionsConfig &selections,
                                      const OperationMetadata &metadata) {
    throw "not implemented, should be implemented by the template";
  };

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

class BaseGraphQLObjectWithID : public BaseQGraphQLObject {
  Q_OBJECT

 protected:
 public:
  const QString id;
};

// stores global node of graphql type and it's retainers.
template <typename T>
class NodeRecord {
  static_assert(std::is_base_of<BaseGraphQLObjectWithID, T>::value,
                "<T> Must derive from BaseGraphQLObjectWithID");
  QSet<QString> m_retainers;
  typedef std::shared_ptr<T> T_sharedQObject;

 public:
  T_sharedQObject node;
  void retain(const QString &operation_name) {
    m_retainers.insert(operation_name);
  }
  void loose(const QString &operation_name) {
    m_retainers.remove(operation_name);
  }
  bool has_retainers() const { return m_retainers.isEmpty(); }
};

template <typename T>

class QGraphQLObjectStore {
  static_assert(std::is_base_of<BaseGraphQLObjectWithID, T>::value,
                "<T> Must derive from BaseGraphQLObjectWithID");
  typedef std::shared_ptr<NodeRecord<T>> T_sharedRecord;

 protected:
  QMap<QString, T_sharedRecord> m_data;

 public:
  std::optional<T_sharedRecord> get_record(const QString &id) {
    if (m_data.contains(id)) {
      return {m_data.value(id).node};
    }
    return {};
  }

  void add_record(const T_sharedRecord &record) {
    m_data.insert(record->node->id, record);
  };

  void loose(const T_sharedRecord::T_sharedQObject &node,
             const QString &operation_name) {
    auto record = m_data.value(node->id);
    record->loose(operation_name);
    if (!record->has_retainers()) {
      m_data.remove(node->id);
      qDebug() << "Node with ID: " << node->id << "has ref count of "
               << node.use_count();
    }
  }
};

}  // namespace qtgql
