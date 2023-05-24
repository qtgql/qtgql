#pragma once
#include <QDateTime>

#include "basecustomscalar.hpp"
namespace qtgql {
namespace customscalars {
class BaseCacheAbleScalar {
 protected:
  QString m_cached_to_qt;
  bool m_should_update = true;
};

class DateTimeScalar : public CustomScalarABC<QDateTime, QString>,
                       BaseCacheAbleScalar {
 public:
  void deserialize(const QJsonValue &raw_data) override;

  const QString &GRAPHQL_NAME() override;

  const QString &to_qt() override;
};

class DateScalar : public CustomScalarABC<QDate, QString>, BaseCacheAbleScalar {
 public:
  void deserialize(const QJsonValue &raw_data) override;

  const QString &GRAPHQL_NAME() override;

  const QString &to_qt() override;
};

class TimeScalar : public CustomScalarABC<QTime, QString>, BaseCacheAbleScalar {
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
};  // namespace customscalars
};  // namespace qtgql
