#pragma once
#include "QAbstractListModel"
#include "Qt"
#include "metadata.hpp"
#include "objecttype.hpp"

namespace qtgql {
namespace bases {

class ListModelMixin : public QAbstractListModel {
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

  static const QModelIndex &invalid_index() {
    static const QModelIndex ret = QModelIndex();
    return ret;
  }

  int m_count = 0;
  int m_current_index = 0;

 public:
  explicit ListModelMixin(QObject *parent = nullptr)
      : QAbstractListModel(parent) {}

  virtual ~ListModelMixin() = default;

  int rowCount(const QModelIndex &parent = QModelIndex()) const override {
    return (!parent.isValid() ? m_count : 0);
  }

  static const int QOBJECT_ROLE = Qt::UserRole + 1;

  QHash<int, QByteArray> roleNames() const override { return c_role_names; }

  void set_current_index(int index) {
    m_current_index = index;
    emit currentIndexChanged();
  }

 signals:

  void countChanged();

  void currentIndexChanged();
};

template <typename T_QObject>
class ListModelABC : public ListModelMixin {
  typedef std::unique_ptr<QList<T_QObject *>> T_QObjectList;

 private:
  void update_count() {
    auto cur_count = m_data->count();
    if (m_count != cur_count) {
      m_count = cur_count;
      emit countChanged();
    }
  };

 protected:
  T_QObjectList m_data;

  void insert_common(const int from, const int to) {
    beginInsertRows(invalid_index(), from, to);
  }

  void end_insert_common() {
    update_count();
    endInsertRows();
  }

  void remove_common(int from, int to) {
    beginRemoveRows(invalid_index(), from, to);
  }

  void end_remove_common() {
    update_count();
    endRemoveRows();
  }

 public:
  explicit ListModelABC(QObject *parent, T_QObjectList data = {})
      : ListModelMixin(parent), m_data{std::move(data)} {
    m_count = m_data->length();
  };

  [[nodiscard]] QVariant data(const QModelIndex &index,
                              int role) const override {
    auto row = index.row();
    if (row < m_count && index.isValid()) {
      if (role == QOBJECT_ROLE) {
        return QVariant::fromValue(static_cast<QObject *>(m_data->value(row)));
      }
    }
    return {};
  }

  T_QObject *get(int index) const { return m_data->value(index); }

  T_QObject *first() const { return m_data->first(); }

  T_QObject *last() const { return m_data->last(); }

  int rowCount(const QModelIndex &parent = QModelIndex()) const override final {
    return m_count;
  }

  void insert(int index, const T_QObject &shared_obj_ref) {
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
    insert_common(index, index);
    m_data->insert(index, shared_obj_ref);
    end_insert_common();
  }

  void append(T_QObject *object) {
    insert_common(m_count, m_count);
    m_data->append(object);
    end_insert_common();
  }

  void pop(int index = -1) {
    bool index_is_valid = (-1 < index && index < m_count);
    int real_index = index_is_valid ? index : (m_count - 1);
    remove_common(real_index, real_index);
    m_data->remove(real_index);
    end_remove_common();
  }

  void clear() {
    if (!m_data->isEmpty()) {
      remove_common(0, m_count - 1);
      m_data->clear();
      end_remove_common();
    }
  }

  // if count == 0 nothing would be removed.
  // rows count starts from 0, for [1, 2, 3] removeRows(1, 2) would cause [1, ].
  bool removeRows(int row, int count,
                  const QModelIndex &parent = QModelIndex()) override {
    if ((row + count) <= m_count) {
      remove_common(row, count);
      m_data->remove(row, count);
      end_remove_common();
      return true;
    }
    return false;
  }
};

}  // namespace bases
}  // namespace qtgql
