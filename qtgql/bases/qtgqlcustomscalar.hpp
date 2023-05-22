#pragma once
#include <QString>

#include "../utils/utils.hpp"
namespace qtgql {
/*
 * T - would be the deserialized type.
 * R_RAW - The Json type of this scalar.
 * T_QtType - the property type that would be exposed to QML, usually this would
 * be a string
 */
template <typename T, typename T_Raw, typename T_QtType>
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

  //    /*
  //     * A place-holder for when a graphql query returned null or the field
  //     wasn't queried.
  //     */
  //    static const T DEFAULT_VALUE(){
  //        static T def;
  //        return def;
  //    }

  CustomScalarABC() : m_value() {}

  explicit CustomScalarABC(const T_Raw &raw_data) {
    throw NotImplementedError({});
  };

  /*
   * Will be used by the property getter, This is the official value that Qt
   * should "understand".
   */
  virtual const T_QtType &to_qt() = 0;

  bool operator==(const CustomScalarABC &other) const {
    return m_value == other.m_value;
  };
  bool operator!=(const CustomScalarABC &other) const {
    return !(operator==(other));
  }
};
}  // namespace qtgql
