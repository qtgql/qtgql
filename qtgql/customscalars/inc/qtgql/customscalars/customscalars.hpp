#pragma once
#include "../../../../../../../../MyConnandeps/Qt/6.5.0/gcc_64/include/QtCore/QDateTime"
#include "basecustomscalar.hpp"

namespace qtgql {
class DateTimeScalar : public CustomScalarABC<QDateTime, QString> {
 private:
  QString m_cached_to_qt;
  bool m_should_update = true;

 public:
  void deserialize(const QJsonValue &raw_data) override;

  const QString &GRAPHQL_NAME() override;

  const QString &to_qt() override;
};

class DecimalScalar : public CustomScalarABC<QString, QString> {
 public:
  void deserialize(const QJsonValue &raw_data) override;
  const QString &GRAPHQL_NAME() override;
  const QString &to_qt() override;
};

}  // namespace qtgql
