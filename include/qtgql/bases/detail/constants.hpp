#pragma once
#include <QUuid>
#include <limits>

namespace qtgql {
namespace bases {
namespace scalars {
typedef std::nullptr_t Void; // represents null value
typedef QString Id;          // GraphQL ID scalar
} // namespace scalars

namespace DEFAULTS {
inline static const QUuid UUID =
    QUuid::fromString("9b2a0828-880d-4023-9909-de067984523c");
inline static const scalars::Id ID = "9b2a0828-880d-4023-9909-de067984523c";
inline static const scalars::Void VOID = scalars::Void();
inline static const QString STRING = "";
inline static const int INT = std::numeric_limits<int>::lowest();
inline static const float FLOAT = std::numeric_limits<float>::lowest();
inline static const bool BOOL = false;
} // namespace DEFAULTS
} // namespace bases
} // namespace qtgql
