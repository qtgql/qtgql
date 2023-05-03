#pragma once
#include <QAbstractListModel>
#include <Qt>

#include "baseqgraphqlobject.hpp"
#include "graphqlmetadata.hpp"

namespace qtgql {
class _QGraphQLListModelMixin : public QAbstractListModel {
  Q_OBJECT

  Q_PROPERTY(int count MEMBER m_count NOTIFY countChanged)
  Q_PROPERTY(int currentIndex MEMBER m_current_index WRITE set_current_index
                 NOTIFY currentIndexChanged)

 private:
  static QHash<int, QByteArray> default_roles() {
    QHash<int, QByteArray> roles;
    roles.insert(Qt::UserRole + 1, "qtObject");
    return roles;
  }

 protected:
  const QHash<int, QByteArray> c_role_names = default_roles();
  static const QModelIndex& invalid_index() {
    static const QModelIndex ret = QModelIndex();
    return ret;
  }

  int m_count = 0;
  int m_current_index = 0;

  void set_current_index(int index) {
    m_current_index = index;
    emit currentIndexChanged();
  }

 public:
  explicit _QGraphQLListModelMixin(QObject* parent = nullptr)
      : QAbstractListModel(parent) {}
  virtual ~_QGraphQLListModelMixin() = default;
  int rowCount(const QModelIndex& parent = QModelIndex()) const override {
    return (!parent.isValid() ? m_count : 0);
  }
  static const int QOBJECT_ROLE = Qt::UserRole + 1;
  QHash<int, QByteArray> roleNames() const override { return c_role_names; }

 signals:
  void countChanged();
  void currentIndexChanged();
};

template <typename T_sharedQObject>
class QGraphQLListModelABC : public _QGraphQLListModelMixin {
  typedef std::unique_ptr<QList<T_sharedQObject>> T_sharedObjectQlist;

 private:
  void update_count() {
    auto cur_count = m_data->count();
    if (m_count != cur_count) {
      m_count = cur_count;
      emit countChanged();
    }
  };

 protected:
  T_sharedObjectQlist m_data;

  void insert_common(const int from, const int to, std::function<void()> func) {
    beginInsertRows(invalid_index(), from, to);
    func();
    update_count();
    endInsertRows();
  }
  void remove_common(const int from, const int to, std::function<void()> func) {
    beginRemoveRows(invalid_index(), from, to);
    func();
    update_count();
    endRemoveRows();
  }

 public:
  explicit QGraphQLListModelABC(
      QObject* parent = nullptr,
      T_sharedObjectQlist data = std::make_unique<QList<T_sharedQObject>>())
      : _QGraphQLListModelMixin(parent), m_data{std::move(data)} {
    m_count = m_data->length();
  };

  QVariant data(const QModelIndex& index, int role) const override {
    auto row = index.row();
    if (row < m_count && index.isValid()) {
      if (role == QOBJECT_ROLE) {
        return QVariant::fromValue(
            static_cast<QObject*>(m_data->at(row).get()));
      }
    }
    return {};
  }
  int rowCount(const QModelIndex& parent = QModelIndex()) const override final {
    return m_count;
  }

  void insert(int index, const T_sharedQObject& shared_obj_ref) {
    if (index > m_count) {
      qWarning() << "index " << index << " is greater than count " << m_count
                 << ". "
                 << "The item will be inserted at the end of the list";
      index = m_count;
    } else if (index < 0) {
      qWarning() << "index " << index << " is lower than 0. "
                 << "The item will be inserted at the beginning of the list";
      index = 0;
    }
    beginInsertRows(invalid_index(), index, index);
    insert_common(index, index, [&] { m_data->insert(index, shared_obj_ref); });
  }

  void append(const T_sharedQObject& shared_obj_ref) {
    insert_common(m_count, m_count,
                  [&]() -> void { m_data->append(shared_obj_ref); });
  }

  void pop(const int index = -1) {
    int real_index = (index > -1 ? index : m_count);
    remove_common(real_index, real_index, [&] { m_data->remove(real_index); });
  }

  void clear() {
    if (!m_data.isEmpty()) {
      remove_common(0, m_count - 1, [&] {
        m_data->clear();
        update_count();
      });
    }
  }

  bool removeRows(int row, int count,
                  const QModelIndex& parent = QModelIndex()) override {
    if ((row + count) <= m_count) {
      remove_common(row, count, [&] { m_data->remove(row, count); });
      return true;
    }
    return false;
  }

  // implemented in the jinja2 template.
  virtual void update(const QList<QJsonObject>& data,
                      const SelectionsConfig& selections) = 0;
};

}  // namespace qtgql
