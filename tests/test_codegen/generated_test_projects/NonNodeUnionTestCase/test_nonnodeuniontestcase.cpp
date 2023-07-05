#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace NonNodeUnionTestCase {
using namespace qtgql;

auto ENV_NAME = QString("NonNodeUnionTestCase");
auto SCHEMA_ADDR = get_server_address("48912056");

TEST_CASE("NonNodeUnionTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = mainquery::MainQuery::shared();
  mq->set_variables({NonNodeUnionTestCase::Enums::UnionChoice::PERSON});
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    auto raw_ptr = mq->data()->get_whoAmI();
    REQUIRE(raw_ptr->property("__typeName").toString().toStdString() ==
            "Person");
    auto p = qobject_cast<const mainquery::Person__whoAmI *>(raw_ptr);
    REQUIRE(!p->get_name().isEmpty());
  };
  SECTION("test update same type") {
    auto person = qobject_cast<const mainquery::Person__whoAmI *>(
        mq->data()->get_whoAmI());
    auto prev_name = mq->data()->get_whoAmI()->property("name").toString();
    auto mq2 = mainquery::MainQuery::shared();
    test_utils::SignalCatcher catcher({.source_obj = person, .only = "name"});
    mq2->set_variables({NonNodeUnionTestCase::Enums::UnionChoice::PERSON});
    mq2->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(mq2);
    REQUIRE(mq->data()

                ->get_whoAmI()
                ->property("name")
                .toString()
                .toStdString() != prev_name.toStdString());
  };
}

}; // namespace NonNodeUnionTestCase
