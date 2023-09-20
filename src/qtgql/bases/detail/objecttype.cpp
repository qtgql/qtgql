#include "objecttype.hpp"

namespace qtgql::bases {

const QString &ObjectTypeABC::__typename() const {
  throw exceptions::NotImplementedError(
      {"Derived classes must override this method."});
};
} // namespace qtgql::bases
