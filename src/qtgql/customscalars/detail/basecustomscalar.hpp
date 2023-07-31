#pragma once
#include <QJsonValue>
#include <QString>

namespace qtgql {
namespace customscalars {
/*
 * T - would be the deserialized type.
 * T_QtType - the property type that would be exposed to QML, usually this would
 * be a string
 */
template <typename T, typename T_QtType> class CustomScalarABC {
protected:
  T m_value;

public:
  // abstract methods
  /*
   * The *real* GraphQL name of the scalar (used by the codegen inspection
   * pipeline)
   */
  virtual const QString &GRAPHQL_NAME() = 0;
  /*
   * Will be used by the property getter, This is the official value that Qt
   * should "understand".
   */
  virtual const T_QtType &to_qt() = 0;
  /*
   * Serialize the scalar. Used for operation variables.
   */
  [[nodiscard]] virtual QJsonValue serialize() const = 0;

  /*
   * Deserializes data fetched from graphql.
   */
  virtual void deserialize(const QJsonValue &raw_data) = 0;
  // end abstract methods

  CustomScalarABC() : m_value() {}
  explicit CustomScalarABC(const T &v) : m_value(v) {}

  bool operator==(const CustomScalarABC &other) const {
    return m_value == other.m_value;
  };

  bool operator!=(const CustomScalarABC &other) const {
    return !(operator==(other));
  }
  bool operator<(const CustomScalarABC &other) const {
    return m_value < other.m_value;
  }
};
}; // namespace customscalars
}; // namespace qtgql
