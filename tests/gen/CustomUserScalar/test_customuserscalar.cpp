#include "gen/MainQuery.hpp"
#include "testframework.hpp"
#include "testutils.hpp"

namespace CustomUserScalar {
using namespace qtgql;

auto ENV_NAME = std::string("CustomUserScalar");

TEST_CASE("CustomUserScalar") {
  auto SCHEMA_ADDR =
      test_utils::get_server_address(QString::fromStdString(ENV_NAME), "http");

  auto env = test_utils::get_or_create_http_env(ENV_NAME, SCHEMA_ADDR);
  auto http_nl =
      dynamic_cast<gqloverhttp::GraphQLOverHttp *>(env->get_network_layer());

  SECTION("test deserialize") {
    auto mq = mainquery::MainQuery::shared();
    http_nl->set_headers({{"country-code", "uk"}});
    mq->execute();
    test_utils::wait_for_completion(mq);
    auto user = mq->data()->get_user();
    auto country = user->get_country();
    REQUIRE(country.toStdString() == "United Kingdom");
    auto country_cpp = user->get_country_cpp();
    REQUIRE(country_cpp->get_value() == "uk");
  };
  SECTION("test update") {
    auto mq = mainquery::MainQuery::shared();
    http_nl->set_headers({{"country-code", "isr"}});
    mq->execute();
    test_utils::wait_for_completion(mq);
    auto user = mq->data()->get_user();
    auto country = user->get_country();
    REQUIRE(country.toStdString() == "Israel");
    auto country_cpp = user->get_country_cpp();
    REQUIRE(country_cpp->get_value() == "isr");
    http_nl->set_headers({{"country-code", "uk"}});
    mq->execute()();
    test_utils::wait_for_completion(mq);
    REQUIRE(user->get_country().toStdString() == "United Kingdom");
    REQUIRE(user->get_country_cpp()->get_value() == "uk");
  };
}

}; // namespace CustomUserScalar
