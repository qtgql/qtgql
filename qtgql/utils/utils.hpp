#pragma once
#include <stdio.h>

#include <QAbstractListModel>
namespace qtgql {
class NotImplementedError : public std::logic_error {
  struct Msg {
    const char* msg = "Function not yet implemented";
  };

 public:
  explicit NotImplementedError(const Msg& msg) : std::logic_error(msg.msg){};
};
}  // namespace qtgql
