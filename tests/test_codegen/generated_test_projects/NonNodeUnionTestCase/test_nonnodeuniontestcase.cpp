#include "debugableclient.hpp"
#include "graphql/__generated__/MainQuery.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace NonNodeUnionTestCase {
using namespace qtgql;

auto ENV_NAME = QString("NonNodeUnionTestCase");
auto SCHEMA_ADDR = get_server_address("3652353");

TEST_CASE("NonNodeUnionTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = mainquery::MainQuery::shared();
  mq->set_variables({NonNodeUnionTestCase::Enums::UnionChoice::PERSON});
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    auto raw_ptr = mq->data()->get_user()->get_whoAmI();
    REQUIRE(raw_ptr->property("__typeName").toString().toStdString() ==
            "Person");
    auto p = qobject_cast<const mainquery::Person__userwhoAmI *>(raw_ptr);
    REQUIRE(p->get_name().toStdString() == "Nir");
  };
  SECTION("test update") { REQUIRE(false); };
}

}; // namespace NonNodeUnionTestCase
