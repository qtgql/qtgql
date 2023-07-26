#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "qtgql/bases/bases.hpp"
#include "qtgql/gqlwstransport/gqlwstransport.hpp"
#include "testutils.hpp"
using namespace qtgql;


QString get_subscription_str(bool raiseOn5 = false,
                             const QString &op_name = "defaultOpName",
                             int target = 10) {
    QString ro5 = raiseOn5 ? "true" : "false";
    return QString("subscription %1 {count(target: %2, raiseOn5: %3) }")
            .arg(op_name, QString::number(target), ro5);
}