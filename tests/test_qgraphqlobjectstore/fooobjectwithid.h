#pragma once
#include "qtgql/bases/bases.hpp"
using namespace qtgql;

class Foo : public bases::ObjectTypeABCWithID {
  const QString m_id;

 public:
  Foo(const QString &id_)
      : bases::ObjectTypeABCWithID::ObjectTypeABCWithID(), m_id(id_){};

  const QString &get_id() const override { return m_id; }

  static auto &INST_STORE() {
    static bases::ObjectStore<Foo> _store;
    return _store;
  }

  void update(const QJsonObject &data,
              const bases::SelectionsConfig &selections) override{};
  void loose(const bases::OperationMetadata &metadata) override{};
};
