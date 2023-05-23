#pragma once
#include "qtgql/bases/objecttype.hpp"

class Foo : public qtgql::ObjectTypeABCWithID {
  const QString m_id;

 public:
  Foo(const QString &id_)
      : qtgql::ObjectTypeABCWithID::ObjectTypeABCWithID(), m_id(id_){};

  const QString &get_id() const override { return m_id; }

  static auto &INST_STORE() {
    static qtgql::ObjectStore<Foo> _store;
    return _store;
  }

  void update(const QJsonObject &data,
              const qtgql::SelectionsConfig &selections) override{};
  void loose(const qtgql::OperationMetadata &metadata) override{};
};
