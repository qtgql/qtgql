#include "testframework.hpp"

#include "qtgql/customscalars/customscalars.hpp"
#include "testutils.hpp"

#include <QObject>

TEST_CASE("Test foo 2") {
    QObject parent_cleaner(nullptr);
//        QObject parent_cleaner;
//    std::vector<QObject *> init_vec;
//    for (int i = 0; i < 10; i++) {
//        init_vec.emplace_back(new QObject(&parent_cleaner));
//    }
//    REQUIRE(parent_cleaner.children().empty());
//auto obj = new QObject(nullptr);

    SECTION("do test"){
        auto obj = new QObject(&parent_cleaner);

        REQUIRE(obj->parent()== nullptr);
    }

//delete obj;
}