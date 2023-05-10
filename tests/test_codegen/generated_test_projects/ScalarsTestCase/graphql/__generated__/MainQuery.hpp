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
  ScalarsTestCase::User* m_inst;

 public:
  int get_age() const { return m_inst->get_age(); };

  float get_agePoint() const { return m_inst->get_agePoint(); };

  const QString& get_id() const { return m_inst->get_id(); };

  bool get_male() const { return m_inst->get_male(); };

  QString get_name() const { return m_inst->get_name(); };

  QUuid get_uuid() const { return m_inst->get_uuid(); };
};

};  // namespace mainquery
