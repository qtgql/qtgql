#pragma once
#include <QAbstractListModel>
#include <QJsonArray>
#include <QJsonObject>
#include <QJsonValue>
#include <QRegularExpression>
#include <functional>

namespace qtgql {
namespace utils {

inline std::optional<QString> get_operation_name(const QString &query) {
  static QRegularExpression re("(subscription|mutation|query)( [0-9a-zA-Z]+)*");
  auto match = re.match(query);
  if (match.hasMatch()) {
    return match.captured(2).trimmed();
  }
  return {};
}

} // namespace utils

} // namespace qtgql
