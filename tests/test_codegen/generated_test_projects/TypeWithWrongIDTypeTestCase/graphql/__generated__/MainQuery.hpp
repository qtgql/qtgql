#pragma once
#include "./schema.hpp"
#include "qtgqloperationhandler.hpp"
namespace mainquery {

const qtgql::OperationMetadata OPERATION_METADATA =
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
  std::shared_ptr<TypeWithWrongIDTypeTestCase::User> m_inst;

 public:
  User__age$agePoint$id$male$name(const QJsonObject &data,
                                  const qtgql::SelectionsConfig &config) {
    m_inst = TypeWithWrongIDTypeTestCase::User::from_json(data, config,
                                                          OPERATION_METADATA);
  }
  const QString &get_name() const { return m_inst->get_name(); };

  const int &get_age() const { return m_inst->get_age(); };

  const float &get_agePoint() const { return m_inst->get_agePoint(); };

  const bool &get_male() const { return m_inst->get_male(); };

  const QString &get_id() const { return m_inst->get_id(); };
};

class MainQuery : public qtgql::QtGqlOperationHandlerABC {
  Q_OBJECT
  Q_PROPERTY(const User__age$agePoint$id$male$name *data READ get_data NOTIFY
                 dataChanged);

  std::unique_ptr<User__age$agePoint$id$male$name> m_data;

  const QString &ENV_NAME() override {
    static const auto ret = QString("TypeWithWrongIDTypeTestCase");
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
                                    "  }"
                                    "}"))){};

  const QUuid &operation_id() const override {
    return m_message_template.op_id;
  }

  void on_next(const QJsonObject &message) override {
    if (!m_data && message.contains("data")) {
      auto data = message.value("data").toObject();
      if (data.contains("user")) {
        m_data = std::make_unique<User__age$agePoint$id$male$name>(
            data.value("user").toObject(), OPERATION_METADATA.selections);
      }
    }
  }
  const User__age$agePoint$id$male$name *get_data() { return m_data.get(); }

 signals:
  void dataChanged();
};

};  // namespace mainquery
