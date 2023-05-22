#pragma once
#include <QDateTime>

#include "qtgqlcustomscalar.hpp"

namespace qtgql {
class DateTimeScalar : public CustomScalarABC<QDateTime, QString, QString> {
 private:
  QString m_cached_to_qt;
  bool m_should_update = true;

 public:
  void deserialize(const QString &raw_data) override;

  const QString &GRAPHQL_NAME() override;

  const QString &to_qt() override;
};
}  // namespace qtgql
