#pragma once
#include <QDateTime>

#include "basecustomscalar.hpp"
namespace qtgql {
namespace customscalars {
class BaseTimeScalar {
protected:
  QString m_cached_to_qt;
  bool m_should_update = true;

public:
  inline static Qt::DateFormat FORMAT = Qt::DateFormat(Qt::ISODate);
};

class DateTimeScalar : public CustomScalarABC<QDateTime, QString>,
                       BaseTimeScalar {
public:
  using CustomScalarABC<QDateTime, QString>::CustomScalarABC;

  void deserialize(const QJsonValue &raw_data) override;

  const QString &GRAPHQL_NAME() override;

  const QString &to_qt() override;

  [[nodiscard]] QJsonValue serialize() const override;
};

class DateScalar : public CustomScalarABC<QDate, QString>, BaseTimeScalar {

public:
  using CustomScalarABC<QDate, QString>::CustomScalarABC;

  void deserialize(const QJsonValue &raw_data) override;

  const QString &GRAPHQL_NAME() override;

  const QString &to_qt() override;
  [[nodiscard]] QJsonValue serialize() const override;
};

class TimeScalar : public CustomScalarABC<QTime, QString>, BaseTimeScalar {
public:
  using CustomScalarABC<QTime, QString>::CustomScalarABC;

  void deserialize(const QJsonValue &raw_data) override;

  const QString &GRAPHQL_NAME() override;

  const QString &to_qt() override;
  [[nodiscard]] QJsonValue serialize() const override;
};

class DecimalScalar : public CustomScalarABC<QString, QString> {
public:
  using CustomScalarABC<QString, QString>::CustomScalarABC;

  void deserialize(const QJsonValue &raw_data) override;

  const QString &GRAPHQL_NAME() override;

  const QString &to_qt() override;
  [[nodiscard]] QJsonValue serialize() const override;
};
}; // namespace customscalars
}; // namespace qtgql
