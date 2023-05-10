#pragma once
#include <QJsonObject>
#include <QObject>
#include <memory>
#include <qtgqlconstants.hpp>
#include <qtgqlmetadata.hpp>
#include <qtgqlobjecttype.hpp>

namespace ScalarsTestCase {

// ----------- Object Types -----------
class User : public qtgql::QtGqlObjectTypeABCWithID {
 protected:
  QString m_id = qtgql::CONSTANTS::ID;
  QString m_name = " - ";
  int m_age = 0;
  float m_agePoint = 0.0;
  bool m_male = false;
  QUuid m_uuid = qtgql::CONSTANTS::UUID;

 signals:
  void idChanged();
  void nameChanged();
  void ageChanged();
  void agePointChanged();
  void maleChanged();
  void uuidChanged();

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

  const float &get_agePoint() const { return m_agePoint; }
  void agePoint_setter(const float &v) {
    m_agePoint = v;
    emit agePointChanged();
  };

  const bool &get_male() const { return m_male; }
  void male_setter(const bool &v) {
    m_male = v;
    emit maleChanged();
  };

  const QUuid &get_uuid() const { return m_uuid; }
  void uuid_setter(const QUuid &v) {
    m_uuid = v;
    emit uuidChanged();
  };

 public:
  inline static const QString TYPE_NAME = "User";
  User(QObject *parent = nullptr)
      : qtgql::QtGqlObjectTypeABCWithID::QtGqlObjectTypeABCWithID(parent){};

  std::shared_ptr<User> from_json(QObject *parent, const QJsonObject &data,
                                  const qtgql::SelectionsConfig &config,
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

    if (config.selections.contains("agePoint") && data.contains("agePoint")) {
      inst->m_agePoint = data.value("agePoint").toDouble();
    };

    if (config.selections.contains("male") && data.contains("male")) {
      inst->m_male = data.value("male").toBool();
    };

    if (config.selections.contains("uuid") && data.contains("uuid")) {
      inst->m_uuid = data.value("uuid").toVariant().toUuid();
    };

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

}  // namespace ScalarsTestCase
