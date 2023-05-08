#pragma once
#include <QJsonObject>
#include <QObject>
#include <memory>
#include <qtgqlconstants.hpp>
#include <qtgqlmetadata.hpp>
#include <qtgqlobjecttype.hpp>
namespace ScalarsTestCase {

// ----------- Object Types -----------

class User : public qtgql::QtGqlObjectTypeABC {
  inline static const QString TYPE_NAME = "User";

 protected:
  QString m_id = qtgql::CONSTANTS::ID;
  QString m_name = " - ";
  int m_age = 0;
  float m_agePoint = 0.0;
  bool m_male = false;
  QUuid m_uuid = qtgql::CONSTANTS::UUID;

 public:
  User(QObject *parent = nullptr) : QObject::QObject(parent){};

 signals:
  void idChanged();
  void nameChanged();
  void ageChanged();
  void agePointChanged();
  void maleChanged();
  void uuidChanged();

 public:
  void id_setter(const QString &v) {
    m_id = v;
    emit idChanged();
  };

  void name_setter(const QString &v) {
    m_name = v;
    emit nameChanged();
  };

  void age_setter(const int &v) {
    m_age = v;
    emit ageChanged();
  };

  void agePoint_setter(const float &v) {
    m_agePoint = v;
    emit agePointChanged();
  };

  void male_setter(const bool &v) {
    m_male = v;
    emit maleChanged();
  };

  void uuid_setter(const QUuid &v) {
    m_uuid = v;
    emit uuidChanged();
  };

 public:
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

    record = NodeRecord(node = inst, retainers = set())
                 .retain(metadata.operation_name);
    cls.__store__.add_record(record);

    return inst;
  };
};

}  // namespace ScalarsTestCase
