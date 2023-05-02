#pragma once

#include <QObject>
#include <QSet>
#include <QSharedData>

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

 public:
  T node;
  void retain(const QString &operation_name) {
    m_retainers.insert(operation_name);
  }
};

template <typename T>

class QGraphQLObjectStore {
  static_assert(std::is_base_of<BaseGraphQLObjectWithID, T>::value,
                "<T> Must derive from BaseGraphQLObjectWithID");
  typedef NodeRecord<T> SharedRecord_T;
  typedef std::shared_ptr<T> Shared_T;

 protected:
  QMap<QString, SharedRecord_T> m_data;

 public:
  std::optional<SharedRecord_T> get_node(const QString &id) {
    if (m_data.contains(id)) {
      return {m_data.value(id).node};
    }
    return {};
  }

  void add_node(const Shared_T &node) { m_data.insert(node.id, node); };
};

}  // namespace qtgql
