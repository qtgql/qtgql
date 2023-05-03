#pragma once
#include <stdio.h>

#include <QAbstractListModel>
namespace qtgql {
class NoHeap {
 private:
  void* operator new(size_t);
  void operator delete(void*);
  void* operator new[](size_t);
  void operator delete[](void*);
};

class QListModelModifier : private NoHeap {
  QListModelModifier() = delete;

 protected:
  QAbstractListModel* m_model;
  const QModelIndex* m_model_index;
  int m_first;
  int m_last;
};

class QListModelInserter : public QListModelModifier {
 public:
  explicit QListModelInserter(QAbstractListModel* model_ptr) {
    m_model = model_ptr;
    m_model->begineInsertRows(m_model_index, m_first, m_last);
  }
  ~QListModelInserter() { m_model->endInsertRows(); }
};

}  // namespace qtgql
