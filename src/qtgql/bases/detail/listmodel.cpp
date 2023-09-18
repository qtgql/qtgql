#include "listmodel.hpp"
namespace qtgql::bases {
QHash<int, QByteArray> ListModelMixin::default_roles() {
  QHash<int, QByteArray> roles;
  roles.insert(Qt::UserRole + 1, "data");
  return roles;
}

const QModelIndex &ListModelMixin::invalid_index() {
  static const QModelIndex ret = QModelIndex();
  return ret;
}

int ListModelMixin::rowCount(const QModelIndex &parent) const {
  return (!parent.isValid() ? m_count : 0);
}

QHash<int, QByteArray> ListModelMixin::roleNames() const {
  return c_role_names;
}

void ListModelMixin::set_current_index(int index) {
  m_current_index = index;
  emit currentIndexChanged();
}

ListModelMixin::ListModelMixin(QObject *parent) : QAbstractListModel(parent){};

} // namespace qtgql::bases
