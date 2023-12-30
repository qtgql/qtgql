#pragma once
#include "QAbstractListModel"
#include "qtgql/qtgql_export.hpp"
#include "types.hpp"

namespace qtgql::bases {

class QTGQL_EXPORT ListModelMixin : public QAbstractListModel {
  Q_OBJECT

  Q_PROPERTY(int count MEMBER m_count NOTIFY countChanged)
  Q_PROPERTY(int currentIndex MEMBER m_current_index WRITE set_current_index
                 NOTIFY currentIndexChanged)

private:
  static QHash<int, QByteArray> default_roles();

protected:
  const QHash<int, QByteArray> c_role_names = default_roles();

  static const QModelIndex &invalid_index();

  int m_count = 0;
  int m_current_index = 0;

public:
  explicit ListModelMixin(QObject *parent = nullptr);

  int rowCount(const QModelIndex &parent = QModelIndex()) const override;

  static const int DATA_ROLE = Qt::UserRole + 1;

  QHash<int, QByteArray> roleNames() const override;

  void set_current_index(int index);

signals:

  void countChanged();

  void currentIndexChanged();
};

template <typename T> struct is_shared_ptr : std::false_type {};
template <typename T>
struct is_shared_ptr<std::shared_ptr<T>> : std::true_type {};

template <typename T> class ListModelABC : public ListModelMixin {
  typedef std::vector<T> T_VEC;

private:
  void update_count() {
    auto cur_count = m_data.size();
    if (m_count != cur_count) {
      m_count = cur_count;
      emit countChanged();
    }
  };
  QVariant p_dataFn(const T &node) const {
    if constexpr (std::is_pointer_v<T>)
      return QVariant::fromValue(qobject_cast<QObject *>(node));
    else
      return node;
  };

protected:
  T_VEC m_data;

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
  explicit ListModelABC(QObject *parent, T_VEC data = {})
      : ListModelMixin(parent), m_data{std::move(data)} {
    m_count = m_data.size();
  };

  [[nodiscard]] QVariant data(const QModelIndex &index,
                              int role) const override {
    auto row = index.row();
    if (row < m_count && index.isValid()) {
      if (role == DATA_ROLE) {
        return p_dataFn(m_data.at(row));
      }
    }
    return {};
  }
  // ──────── ITERATOR ──────────
public:
  using T_const_iterator = T_VEC::const_iterator;
  T_const_iterator begin() const { return m_data.begin(); }
  T_const_iterator end() const { return m_data.end(); }
  // C++ API
public:
  [[nodiscard]] const auto &get(int index) const { return m_data.at(index); }

  [[nodiscard]] const auto &first() const { return m_data.front(); }

  [[nodiscard]] const auto &last() const { return m_data.back(); }

  int rowCount(const QModelIndex &parent = {}) const override {
    return m_count;
  }

  void replace(std::size_t i, const T &value) {
    if (i < m_count) {
      insert_common(i, i);
      m_data.at(i) = value;
      end_insert_common();
    }
  }

  void append(const T &element) {
    insert_common(m_count, m_count);
    m_data.push_back(element);
    end_insert_common();
  }

  // removes item at index. if index is -1 removes from the end of the vec.
  void pop(int index = -1) {
    if (m_data.empty()) {
      return;
    }
    bool index_is_valid = (-1 < index && index < m_count);
    int real_index = index_is_valid ? index : (m_count - 1);

    remove_common(real_index, real_index);
    m_data.erase(std::next(m_data.begin(), real_index));
    end_remove_common();
  }

  void clear() {
    if (!m_data.empty()) {
      remove_common(0, m_count - 1);
      m_data.clear();
      end_remove_common();
    }
  }

  /* if count == 0 nothing would be removed.
   rows count starts from 0, for [1, 2, 3] removeRows(1, 2) would cause [1, ].
   */
  bool removeRows(int row, int count,
                  const QModelIndex &parent = QModelIndex()) override {
    if ((row + count) <= m_count) {
      remove_common(row, row + count);
      m_data.erase(std::next(m_data.begin(), row),
                   std::next(m_data.begin(), row + count));
      end_remove_common();
      return true;
    }
    return false;
  }
};

} // namespace qtgql::bases
