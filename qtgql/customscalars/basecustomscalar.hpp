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
template <typename T, typename T_QtType>
class CustomScalarABC {
 protected:
  T m_value;

  /*
   * Deserializes data fetched from graphql.
   */

 public:
  /*
   * The *real* GraphQL name of the scalar (used by the codegen inspection
   * pipeline)
   */
  virtual const QString &GRAPHQL_NAME() = 0;

  CustomScalarABC() : m_value() {}

  /*
   * Will be used by the property getter, This is the official value that Qt
   * should "understand".
   */
  virtual const T_QtType &to_qt() = 0;

  virtual void deserialize(const QJsonValue &raw_data) = 0;

  bool operator==(const CustomScalarABC &other) const {
    return m_value == other.m_value;
  };

  bool operator!=(const CustomScalarABC &other) const {
    return !(operator==(other));
  }
};
};  // namespace customscalars
};  // namespace qtgql
