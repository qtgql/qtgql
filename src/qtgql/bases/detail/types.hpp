#pragma once
#include "QDebug"
#include "QObject"
#include "QSet"
#include "exceptions.hpp"
#include "qtgql/qtgql_export.hpp"
#include <QUuid>

namespace qtgql::bases {
namespace scalars {
typedef std::nullptr_t Void; // represents null value
typedef QString Id;          // GraphQL ID scalar
};                           // namespace scalars
namespace DEFAULTS {
struct INT {
  static auto value() { return std::numeric_limits<int>::lowest(); };
};
struct FLOAT {
  static auto value() { return std::numeric_limits<float>::lowest(); };
};
struct UUID {
  static auto value() {
    return QUuid::fromString("9b2a0828-880d-4023-9909-de067984523c");
  };
};
struct STRING {
  static auto value() { return QString(""); };
};
struct BOOLEAN {
  constexpr static auto value() { return false; };
};
struct ID {
  static auto value() {
    static auto ret = scalars::Id("9b2a0828-880d-4023-9909-de067984523c");
    return ret;
  };
};
struct VOID {
  static auto value() { return nullptr; };
};

}; // namespace DEFAULTS
template <class T_self, class T, class default_> struct p_Delegates {
  typedef T T_Delegated;
  T_Delegated value = default_::value();
  explicit p_Delegates(const T_Delegated &val) : value(val){};
  static std::shared_ptr<T_self> create(const T &value_) {
    return std::make_shared<T_self>(value_);
  };
  bool operator==(const T_self &other) const { return value == other.value; };
  bool operator<=(const T_self &other) const { return value <= other.value; };
  bool operator>=(const T_self &other) const { return value >= other.value; };
  bool operator==(const T &other) const { return value == other; };
  bool operator<=(const T &other) const { return value <= other; };
  bool operator>=(const T &other) const { return value >= other; };
};
struct GraphQLType {
  virtual const QString __typename() const {
    throw exceptions::NotImplementedError(
        {"Derived classes must override this method."});
  };
};
struct Int : public GraphQLType, p_Delegates<Int, int, DEFAULTS::INT> {
  using p_Delegates::p_Delegates;

  [[nodiscard]] const QString __typename() const override { return "Int"; };
};
struct Float : public GraphQLType, p_Delegates<Float, float, DEFAULTS::FLOAT> {
  using p_Delegates::p_Delegates;

  [[nodiscard]] const QString __typename() const override { return "Float"; };
};
struct UUID : public GraphQLType, p_Delegates<UUID, QUuid, DEFAULTS::UUID> {
  using p_Delegates::p_Delegates;

  [[nodiscard]] const QString __typename() const override { return "UUID"; };
};
struct String : public GraphQLType,
                p_Delegates<String, QString, DEFAULTS::STRING> {
  using p_Delegates::p_Delegates;

  [[nodiscard]] const QString __typename() const override { return "String"; };
};

struct Boolean : public GraphQLType,
                 p_Delegates<Boolean, bool, DEFAULTS::BOOLEAN> {
  using p_Delegates::p_Delegates;

  [[nodiscard]] const QString __typename() const override { return "Boolean"; };
};

struct ID : public GraphQLType, p_Delegates<ID, scalars::Id, DEFAULTS::ID> {
  using p_Delegates::p_Delegates;

  [[nodiscard]] const QString __typename() const override { return "ID"; };
};
struct Void : public GraphQLType,
              p_Delegates<Void, scalars::Void, DEFAULTS::VOID> {
  using p_Delegates::p_Delegates;
  [[nodiscard]] const QString __typename() const override { return "Void"; };
};

class QTGQL_EXPORT ObjectTypeABC : public QObject, GraphQLType {
  Q_OBJECT

  Q_PROPERTY(const QString __typename READ __typename CONSTANT)
public:
  using QObject::QObject;
};

class NodeInterfaceABC;

class QTGQL_EXPORT NodeInterfaceABC : public ObjectTypeABC {
public:
  using ObjectTypeABC::ObjectTypeABC;

  [[nodiscard]] virtual std::shared_ptr<qtgql::bases::ID> get_id() const = 0;
};

} // namespace qtgql::bases
