#pragma once
#include "QDebug"
#include "QObject"
#include "QSet"
#include "metadata.hpp"
#include "./constants.hpp"

namespace qtgql {
namespace bases {

class ObjectTypeABC : public QObject {
  Q_OBJECT

  Q_PROPERTY(QString __typeName READ getTypeName CONSTANT)
  inline static QString __TYPE_NAME = "__NOT_IMPLEMENTED__";

private:
  [[nodiscard]] inline virtual const QString & getTypeName() const { return __TYPE_NAME; }

public:
  using QObject::QObject;
};

class NodeInterfaceABC;

    class NodeInterfaceABC : public ObjectTypeABC {
public:
  using ObjectTypeABC::ObjectTypeABC;

  [[nodiscard]] virtual const scalars::Id &get_id() const = 0;

  // updates a node based on new GraphQL data.
  virtual void update(const QJsonObject &data,
                      const SelectionsConfig &selections, const OperationMetadata &metadata) = 0;
};




} // namespace bases
} // namespace qtgql
