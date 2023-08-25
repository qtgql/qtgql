#include "graphql/__generated__/MainQuery.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace ScalarArgumentsTestCase {
using namespace qtgql;

auto ENV_NAME = QString("ScalarArgumentsTestCase");
auto SCHEMA_ADDR = get_server_address("ScalarArgumentsTestCase");

TEST_CASE("ScalarArgumentsTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") {
    auto mq = mainquery::MainQuery::shared();
    int int_exp = 123;
    float float_exp = 123.123;
    QString string_exp("foobar");
    auto uuid_exp = QUuid::createUuid();
    mq->set_variables({int_exp, float_exp, string_exp, false, uuid_exp});
    mq->fetch();
    test_utils::wait_for_completion(mq);
    auto container = mq->data()->get_getContainer();
    REQUIRE(container->get_i() == int_exp);
    REQUIRE(container->get_f() == float_exp);
    REQUIRE(container->get_string().toStdString() == string_exp.toStdString());
    REQUIRE(container->get_uuid().toString().toStdString() ==
            uuid_exp.toString().toStdString());
  };
  SECTION("test update") { REQUIRE(false); };
}

}; // namespace ScalarArgumentsTestCase
