#pragma once
#include "./schema.hpp"
#include "qtgqloperationhandler.hpp"
namespace mainquery {

class User__id$name$age$agePoint$male$uuid {
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
  ScalarsTestCase::User *m_inst;

 public:
  const QString &get_id() const { return m_inst->get_id(); };

  const QString &get_name() const { return m_inst->get_name(); };

  const int &get_age() const { return m_inst->get_age(); };

  const float &get_agePoint() const { return m_inst->get_agePoint(); };

  const bool &get_male() const { return m_inst->get_male(); };

  const QUuid &get_uuid() const { return m_inst->get_uuid(); };
};

class MainQuery : qtgql::QtGqlOperationHandlerABC {
  Q_OBJECT
  Q_PROPERTY(User__id$name$age$agePoint$male$uuid data MEMBER m_data NOTIFY
                 dataChanged);

  User__id$name$age$agePoint$male$uuid m_data;

  const QString &ENV_NAME() override {
    static const auto ret = QString("ScalarsTestCase");
    return ret;
  }
};

};  // namespace mainquery
