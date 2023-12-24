#pragma once
#include <QString>
#include <catch2/catch_test_macros.hpp>
namespace Catch {
template <> struct StringMaker<QString> {
  static std::string convert(QString const &value) {
    if (value.isEmpty())
      return "\"\"";
    return value.toStdString();
  }
};
} // namespace Catch
