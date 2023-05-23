#pragma once
#include <QJsonObject>
#include <QObject>
#include <memory>
#include <qtgql/bases/constants.hpp>
#include <qtgql/bases/metadata.hpp>
#include <qtgql/bases/objecttype.hpp>
#include <qtgql/customscalars/customscalars.hpp>

namespace DecimalTestCase {

// ----------- Object Types -----------
class User : public qtgql::ObjectTypeABCWithID {
 protected:
  static auto &INST_STORE() {
    static qtgql::ObjectStore<User> _store;
    return _store;
  }

 protected:
  QString m_id = qtgql::CONSTANTS::ID;
  QString m_name = " - ";
  int m_age = 0;
  qtgql::DecimalScalar m_balance = {};

 signals:
  void idChanged();
  void nameChanged();
  void ageChanged();
  void balanceChanged();

 public:
  const QString &get_id() const { return m_id; }

  void id_setter(const QString &v) {
    m_id = v;
    emit idChanged();
  };

  const QString &get_name() const { return m_name; }

  void name_setter(const QString &v) {
    m_name = v;
    emit nameChanged();
  };

  const int &get_age() const { return m_age; }

  void age_setter(const int &v) {
    m_age = v;
    emit ageChanged();
  };

  const QString &get_balance() { return m_balance.to_qt(); }

  void balance_setter(const qtgql::DecimalScalar &v) {
    m_balance = v;
    emit balanceChanged();
  };

 public:
  inline static const QString TYPE_NAME = "User";
  User(QObject *parent = nullptr)
      : qtgql::ObjectTypeABCWithID::ObjectTypeABCWithID(parent){};

  static std::shared_ptr<User> from_json(
      const QJsonObject &data, const qtgql::SelectionsConfig &config,
      const qtgql::OperationMetadata &metadata) {
    auto inst = std::make_shared<User>();

    if (config.selections.contains("id") && data.contains("id")) {
      inst->m_id = data.value("id").toString();
    };

    if (config.selections.contains("name") && data.contains("name")) {
      inst->m_name = data.value("name").toString();
    };

    if (config.selections.contains("age") && data.contains("age")) {
      inst->m_age = data.value("age").toInt();
    };

    if (config.selections.contains("balance") && data.contains("balance")) {
      inst->m_balance = qtgql::DecimalScalar();
      inst->m_balance.deserialize(data.value("balance"));
    };

    auto record = std::make_shared<qtgql::NodeRecord<User>>(inst);
    record->retain(metadata.operation_name);
    INST_STORE().add_record(record);

    return inst;
  };

  void loose(const qtgql::OperationMetadata &metadata) {
    throw "not implemented";
  };
  void update(const QJsonObject &data,
              const qtgql::SelectionsConfig &selections) {
    throw "not implemented";
  };
};

}  // namespace DecimalTestCase
