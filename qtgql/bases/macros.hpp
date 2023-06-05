#pragma once

//  macros can't use namespaces
#define GraphQLEnum_MACRO(T_EnumType)                       \
  inline static const QString name_by_value(T_EnumType v) { \
    for (const auto& member : members) {                    \
      if (member.second == v) {                             \
        return member.first;                                \
      }                                                     \
    }                                                       \
    throw std::runtime_error("Couldn't find enum member");  \
  };                                                        \
                                                            \
  inline static T_EnumType by_name(const QString& name) {   \
    for (const auto& member : members) {                    \
      if (member.first == name) {                           \
        return member.second;                               \
      }                                                     \
    }                                                       \
    throw std::runtime_error("Couldn't find enum member");  \
  }

#define QTGQL_STATIC_MAKE_SHARED(type)                  \
  [[nodiscard]] static std::shared_ptr<type> shared() { \
    return std::make_shared<type>();                    \
  };
