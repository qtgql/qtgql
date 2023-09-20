#include "testframework.hpp"
//#include <QString>
//#include <QTest>
//
//#include "qtgql/customscalars/customscalars.hpp"
//#include "testutils.hpp"

#include <QObject>

TEST_CASE("ListModelABC modifications and operations") {
//    auto parent_cleaner = new QObject(nullptr);
//        QObject parent_cleaner;
//    std::vector<QObject *> init_vec;
//    for (int i = 0; i < 10; i++) {
//        init_vec.emplace_back(new QObject(&parent_cleaner));
//    }
//    REQUIRE(parent_cleaner.children().empty());
//auto obj = new QObject(nullptr);
    auto obj = std::make_unique<QObject>();

    SECTION("do test") {
        REQUIRE(false);
        REQUIRE_EQ(obj->parent(), nullptr);

    }
}
//delete parent_cleaner;
