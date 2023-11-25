#include "gen/MainQuery.hpp"
#include "testframework.hpp"
#include "testutils.hpp"

namespace CustomUserScalar {
using namespace qtgql;

auto ENV_NAME = std::string("CustomUserScalar");
auto SCHEMA_ADDR =
    test_utils::get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("CustomUserScalar") {
  test_utils::get_or_create_env(
      ENV_NAME,
      test_utils::DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") {
    auto mq = mainquery::MainQuery::shared();
    mq->fetch();
    test_utils::wait_for_completion(mq);
    auto user = mq->data()->get_user();
    auto country = user->get_country();
    REQUIRE(country.toStdString() == "United Kingdom");
    auto country_cpp = user->get_country_cpp();
    REQUIRE(country_cpp->get_value() == "uk");
  };
  SECTION("test update") {
    auto mq = mainquery::MainQuery::shared();
    mq->fetch();
    test_utils::wait_for_completion(mq);
    auto user = mq->data()->get_user();
    auto country = user->get_country();
    REQUIRE(country.toStdString() == "Israel");
    auto country_cpp = user->get_country_cpp();
    REQUIRE(country_cpp->get_value() == "isr");
    mq->refetch();
    test_utils::wait_for_completion(mq);
    REQUIRE(user->get_country().toStdString() == "United Kingdom");
    REQUIRE(user->get_country_cpp()->get_value() == "uk");
  };
}

}; // namespace CustomUserScalar
