#include "./schema.hpp"

namespace mainquery {

class User__name$uuid$agePoint$id$age$male : public QObject {
  Q_OBJECT
  ScalarsTestCase::User* m_inst;

 public:
  QString get_name() const { return m_inst->get_name(); };

  QUuid get_uuid() const { return m_inst->get_uuid(); };

  float get_agePoint() const { return m_inst->get_agePoint(); };

  QString get_id() const { return m_inst->get_id(); };

  int get_age() const { return m_inst->get_age(); };

  bool get_male() const { return m_inst->get_male(); };
};

};  // namespace mainquery
