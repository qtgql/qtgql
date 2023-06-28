#pragma once
#include "./constants.hpp"
#include "QDebug"
#include "QObject"
#include "QSet"
#include "metadata.hpp"

namespace qtgql {
namespace bases {

class ObjectTypeABC : public QObject {
  Q_OBJECT

  Q_PROPERTY(QString __typeName READ TYPE_NAME CONSTANT)

public:
  using QObject::QObject;

  [[nodiscard]] inline virtual const QString &TYPE_NAME() {
    throw exceptions::NotImplementedError(
        {"Derived classes must override this method."});
  }
};

class NodeInterfaceABC;

class NodeInterfaceABC : public ObjectTypeABC {
public:
  using ObjectTypeABC::ObjectTypeABC;

  [[nodiscard]] virtual const scalars::Id &get_id() const = 0;
};

} // namespace bases
} // namespace qtgql
