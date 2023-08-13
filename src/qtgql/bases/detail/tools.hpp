#pragma once
#include <QJsonArray>
#include <QJsonObject>
#include <QJsonValue>
#include <string>
#include <unordered_map>
#include "backports.hpp"

namespace qtgql::bases::tools {

struct ArgsMap {
  std::unordered_map<std::string, QJsonValue> m_map;

public:
  inline bool operator==(const ArgsMap &rhs) const {
    return m_map == rhs.m_map;
  }

  QJsonValue at(const std::string &key) { return m_map.at(key); }

  void emplace(const std::string &key, const QJsonValue &value) {
    m_map.emplace(key, value);
  }
};
// shamelessly copied from https://stackoverflow.com/a/2595226/16776498
    template <class T> inline void hash_combine(std::size_t &seed, const T &v) {
        std::hash<T> hasher;
        seed ^= hasher(v) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
    }

    struct QJsonValueHasher {
        std::size_t operator()(const QJsonValue &v) const noexcept {
            switch (v.type()) {
                case QJsonValue::Type::Bool:
                    return std::hash<bool>{}(v.toBool());
                case QJsonValue::Type::String:
                    return std::hash<std::string>{}(v.toString().toStdString());
                case QJsonValue::Type::Double:
                    return std::hash<double>{}(v.toDouble());
                case QJsonValue::Type::Array: {
                    std::size_t ret = 0;
                    for (const QJsonValue value : v.toArray()) {
                        hash_combine(ret, QJsonValueHasher()(value));
                    }
                    return ret;
                }
                case QJsonValue::Type::Object: {
                    std::size_t ret = 0;
                    auto obj = v.toObject();
                    for (const auto &key : obj) {
                        auto key_as_str = key.toString();
                        hash_combine(ret, std::hash<QString>{}(key_as_str));
                        hash_combine(ret, QJsonValueHasher()(obj.value(key_as_str)));
                    }
                    return ret;
                }
                default:
                    return 0;
            }
        }
    };


    struct ArgsMapHasher{
        std::size_t
        operator()(const qtgql::bases::tools::ArgsMap &inst) const noexcept {
            std::size_t ret = 0;
            for (const auto &[k, v] : inst.m_map) {
                hash_combine(ret, std::hash<std::string>{}(k));
                hash_combine(ret, QJsonValueHasher()(inst.m_map.at(k)));
            }
            return ret;
        }
    };
    template<typename T_MAP, typename T_KeyType>
     auto get_or_nullopt(const T_MAP & map, const T_KeyType & key){
        if (backports::map_contains(map, key)){
            return map.at(key);
        }
        return std::nullopt;
    }
} // namespace qtgql::bases::tools



