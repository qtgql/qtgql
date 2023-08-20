#pragma once
#include <unordered_map>

namespace qtgql::bases::backports {
template <typename T_MAP, typename T_KeyType>
bool map_contains(const T_MAP &map, const T_KeyType &key) {
// since C++ 20 there is unordered_map.contains
#if __cplusplus >= 202002L
  return map.contains(key);
#elif
  auto search = map.find(key);
  return search != map.end();
#endif
}
} // namespace qtgql::bases::backports
