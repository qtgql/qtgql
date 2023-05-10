#pragma once
#include <qtgqlobjecttype.hpp>

class Foo;
class Foo : public qtgql::QtGqlObjectTypeABCWithID {
  const QString m_id;

 public:
  Foo(const QString &id_)
      : qtgql::QtGqlObjectTypeABCWithID::QtGqlObjectTypeABCWithID(),
        m_id(id_){};

  const QString &get_id() const override { return m_id; }
  inline static qtgql::QGraphQLObjectStore<Foo> __store__ = {};

  void update(const QJsonObject &data,
              const qtgql::SelectionsConfig &selections) override{};
  void loose(const qtgql::OperationMetadata &metadata) override{};
};
