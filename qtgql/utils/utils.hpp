#pragma once
#include <stdio.h>

#include <QAbstractListModel>
#include <QRegularExpression>
namespace qtgql {
namespace utils {

inline std::optional<QString> get_operation_name(const QString& query) {
  static QRegularExpression re("(subscription|mutation|query)( [0-9a-zA-Z]+)*");
  auto match = re.match(query);
  if (match.hasMatch()) {
    return match.captured(2).trimmed();
  }
  return {};
}

class NotImplementedError : public std::logic_error {
  struct Msg {
    const char* msg = "Function not yet implemented";
  };

 public:
  explicit NotImplementedError(const Msg& msg) : std::logic_error(msg.msg){};
};
}  // namespace utils

}  // namespace qtgql
