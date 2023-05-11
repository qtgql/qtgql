#include "./schema.hpp"

namespace mainquery {

class User__age$agePoint$id$male$name$uuid {
  /*
  User {
    age
     agePoint
     id
     male
     name
     uuid
  }
   */
  Q_GADGET
  ScalarsTestCase::User *m_inst;

 public:
  const int &get_age() const { return m_inst->get_age(); };

  const float &get_agePoint() const { return m_inst->get_agePoint(); };

  const QString &get_id() const { return m_inst->get_id(); };

  const bool &get_male() const { return m_inst->get_male(); };

  const QString &get_name() const { return m_inst->get_name(); };

  const QUuid &get_uuid() const { return m_inst->get_uuid(); };
};

};  // namespace mainquery
