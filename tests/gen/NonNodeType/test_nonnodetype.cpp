#include "gen/MainQuery.hpp"
#include "testframework.hpp"
#include "testutils.hpp"
#include <QSignalSpy>

namespace NonNodeType {
using namespace qtgql;

auto ENV_NAME = std::string("NonNodeType");
auto SCHEMA_ADDR =
    test_utils::get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("NonNodeType") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME,
      test_utils::DebugWsClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto mq = mainquery::MainQuery::shared();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  SECTION("test deserialize") {
    REQUIRE(!mq->data()->get_user()->get_name().isEmpty());
  };
  SECTION("test update") {
    auto prev_name = mq->data()->get_user()->get_name();
    auto mq2 = mainquery::MainQuery::shared();
    mq2->fetch();
    test_utils::wait_for_completion(mq2);
    auto new_name = mq2->data()->get_user()->get_name();
    qDebug() << new_name << "old name is " << prev_name;
    REQUIRE(prev_name != new_name);
    REQUIRE(new_name == mq->data()->get_user()->get_name());
  };
}

}; // namespace NonNodeType
