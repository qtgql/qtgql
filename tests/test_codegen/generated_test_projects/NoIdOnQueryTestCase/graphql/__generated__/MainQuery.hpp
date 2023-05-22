#pragma once
#include "./schema.hpp"
#include "qtgqloperationhandler.hpp"
namespace NoIdOnQueryTestCase {
namespace mainquery {

inline const qtgql::OperationMetadata OPERATION_METADATA =
    qtgql::OperationMetadata{"MainQuery",
                             {

                                 {

                                     {"age", {}},
                                     {"agePoint", {}},
                                     {"id", {}},
                                     {"male", {}},
                                     {"name", {}},
                                 },

                             }};

class User__age$agePoint$id$male$name$uuid {
  /*
  User {
    id
     name
     age
     agePoint
     male
     uuid
  }
   */
  Q_GADGET
  std::shared_ptr<NoIdOnQueryTestCase::User> m_inst;

 public:
  User__age$agePoint$id$male$name$uuid(const QJsonObject &data,
                                       const qtgql::SelectionsConfig &config) {
    m_inst =
        NoIdOnQueryTestCase::User::from_json(data, config, OPERATION_METADATA);
  }
  inline const QString &get_id() const { return m_inst->get_id(); };

  inline const QString &get_name() const { return m_inst->get_name(); };

  inline const int &get_age() const { return m_inst->get_age(); };

  inline const float &get_agePoint() const { return m_inst->get_agePoint(); };

  inline const bool &get_male() const { return m_inst->get_male(); };

  inline const QUuid &get_uuid() const { return m_inst->get_uuid(); };
};

class User__age$agePoint$id$male$name {
  /*
  User {
    name
     age
     agePoint
     male
     id
  }
   */
  Q_GADGET
  std::shared_ptr<NoIdOnQueryTestCase::User> m_inst;

 public:
  User__age$agePoint$id$male$name(const QJsonObject &data,
                                  const qtgql::SelectionsConfig &config) {
    m_inst =
        NoIdOnQueryTestCase::User::from_json(data, config, OPERATION_METADATA);
  }
  inline const QString &get_name() const { return m_inst->get_name(); };

  inline const int &get_age() const { return m_inst->get_age(); };

  inline const float &get_agePoint() const { return m_inst->get_agePoint(); };

  inline const bool &get_male() const { return m_inst->get_male(); };

  inline const QString &get_id() const { return m_inst->get_id(); };
};

class MainQuery : public qtgql::QtGqlOperationHandlerABC {
  Q_OBJECT
  Q_PROPERTY(const *data READ get_data NOTIFY dataChanged);

  std::unique_ptr<> m_data;

  inline const QString &ENV_NAME() override {
    static const auto ret = QString("NoIdOnQueryTestCase");
    return ret;
  }

 public:
  MainQuery()
      : qtgql::QtGqlOperationHandlerABC(qtgql::GqlWsTrnsMsgWithID(
            qtgql::OperationPayload("query MainQuery {"
                                    "  user {"
                                    "    name"
                                    "    age"
                                    "    agePoint"
                                    "    male"
                                    "    id"
                                    "  }"
                                    "}"))){};

  inline const QUuid &operation_id() const override {
    return m_message_template.op_id;
  }

  void on_next(const QJsonObject &message) override {
    if (!m_data && message.contains("data")) {
      auto data = message.value("data").toObject();
      if (data.contains("user")) {
        m_data = std::make_unique<>(data.value("user").toObject(),
                                    OPERATION_METADATA.selections);
      }
    }
  }
  inline const *get_data() { return m_data.get(); }

 signals:
  void dataChanged();
};
};  // namespace mainquery
};  // namespace NoIdOnQueryTestCase
