#pragma once
#include <QHash>
#include <QSet>
#include <QVariant>
#include <QtCore>
#include <concepts>

class BaseQGraphQLObject : public QObject {
  // The Concrete GraphQL object Type.
  static QString TYPE_NAME;

  // Creates a new instance from GraphQL raw data
  virtual BaseQGraphQLObject from_dict(QObject* parent, QVariantMap data) = 0;

  // updates a node based on new GraphQL data.
  virtual void update(QVariantMap data) = 0;

  // releases all child objects if exists.
  // note that this method would be useful only if the object (or one
  // of its children) has an id and a reference in the store,
  // otherwise the pointer to this object is release and this object
  // would be deleted.
  virtual void loose() = 0;
};

class BaseQGraphQLObjectWithID : public BaseQGraphQLObject {
  QString m_id;
};

template <typename T>
concept HasID = std::is_base_of<BaseQGraphQLObjectWithID, T>::value;

template <HasID T>
struct NodeRecord {
  T* node;
  QSet<QString> retainters;

 public:
  // obtain possession for this operation identifier.
  NodeRecord retain(QString operation_name) {
    this->retainters.insert(operation_name);
    return this;
  }
};

template <HasID T>
class QGraphQLObjectRecordStore {
 private:
  QHash<QString, NodeRecord<T>> m_recordes;

 public:
  NodeRecord<T>* getRecord(QString id) {
    if (m_recordes.contains(id)) {
      return m_recordes.value(id);
    };
  };

  void addRecord(NodeRecord<T>* record) {
    m_recordes.insert(record->node.m_id);
  };
  void loose(T* node, QString operation_name) {
    NodeRecord<T>* record = m_recordes.value(node->m_id, nullptr);
    if (record) {
      record->retainters.remove(operation_name);
      if (record->retainters.isEmpty()) {
        m_recordes.remove(record->node.m_id);
        node->deleteLater();
      };
    };
  };
};
