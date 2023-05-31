#pragma once
#include <QString>

#define GraphQLEnum(T_EnumType)                             \
  inline static const QString name_by_value(T_EnumType v) { \
    for (const auto& member : members) {                    \
      if (member.second == v) {                             \
        return member.first;                                \
      };                                                    \
    };                                                      \
  };                                                        \
                                                            \
  inline static T_EnumType by_name(const QString& name) {   \
    for (const auto& member : members) {                    \
      if (member.first == name) {                           \
        return member.second;                               \
      };                                                    \
    };                                                      \
  }

//  }  // namespace bases
//}  // namespace bases
