#pragma once

namespace qtgql {
namespace utils {
template <class... Types> struct TupleQJsonValueComparator {
  bool operator()(const std::tuple<Types...> &lhs,
                  const std::tuple<Types...> &rhs) const {
    return lhs == rhs;
  }
};
} // namespace utils

} // namespace qtgql
