#pragma once
#include "basecustomscalar.hpp"
#include "qtgql/qtgql_export.hpp"
#include <QDateTime>

namespace qtgql::customscalars {
class QTGQL_EXPORT BaseTimeScalar {
protected:
  QString m_cached_to_qt;
  bool m_should_update = true;

public:
  inline static Qt::DateFormat FORMAT = Qt::DateFormat(Qt::ISODate);
};

class QTGQL_EXPORT DateTimeScalar : public CustomScalarABC<QDateTime, QString>,
                                    BaseTimeScalar {
public:
  using CustomScalarABC<QDateTime, QString>::CustomScalarABC;

  void deserialize(const QJsonValue &raw_data) override;

  const QString &GRAPHQL_NAME() override;

  const QString &to_qt() override;

  [[nodiscard]] QJsonValue serialize() const override;
};

class QTGQL_EXPORT DateScalar : public CustomScalarABC<QDate, QString>,
                                BaseTimeScalar {

public:
  using CustomScalarABC<QDate, QString>::CustomScalarABC;

  void deserialize(const QJsonValue &raw_data) override;

  const QString &GRAPHQL_NAME() override;

  const QString &to_qt() override;
  [[nodiscard]] QJsonValue serialize() const override;
};

class QTGQL_EXPORT TimeScalar : public CustomScalarABC<QTime, QString>,
                                BaseTimeScalar {
public:
  using CustomScalarABC<QTime, QString>::CustomScalarABC;

  void deserialize(const QJsonValue &raw_data) override;

  const QString &GRAPHQL_NAME() override;

  const QString &to_qt() override;
  [[nodiscard]] QJsonValue serialize() const override;
};

class QTGQL_EXPORT DecimalScalar : public CustomScalarABC<QString, QString> {
public:
  using CustomScalarABC<QString, QString>::CustomScalarABC;

  void deserialize(const QJsonValue &raw_data) override;

  const QString &GRAPHQL_NAME() override;

  const QString &to_qt() override;
  [[nodiscard]] QJsonValue serialize() const override;
};
}; // namespace qtgql::customscalars
