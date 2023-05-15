#include "MainQuery.hpp"

namespace mainquery {
const QString &MainQuery::ENV_NAME() {
  static const auto ret = QString("ScalarsTestCase");
  return ret;
}

}  // namespace mainquery
