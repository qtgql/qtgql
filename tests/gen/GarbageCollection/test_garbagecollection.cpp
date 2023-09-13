#include "gen/MainQuery.hpp"
#include "testframework.hpp"
#include "testutils.hpp"
#include <QSignalSpy>

namespace GarbageCollection {
using namespace qtgql;

auto ENV_NAME = std::string("GarbageCollection");
auto SCHEMA_ADDR = get_server_address(QString::fromStdString(ENV_NAME));
using namespace std::chrono_literals;
std::shared_ptr<GarbageCollection::User> get_shared_user() {
  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  test_utils::wait_for_completion(mq);
  auto node_id = mq->data()->get_constUser()->get_id();
  REQUIRE(mq.use_count() == 1);
  return GarbageCollection::User::get_node(node_id).value();
}
TEST_CASE("GarbageCollection") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME,
      DebugClientSettings{.prod_settings =
                              {
                                  .url = SCHEMA_ADDR,
                              }},
      100ms);
  SECTION("Test Garbage collection") {

    std::weak_ptr<GarbageCollection::User> weak_user = get_shared_user();
    GarbageCollection::Query::instance()->m_constUser = {};
    // at map
    REQUIRE(weak_user.use_count() == 1);
    REQUIRE(QTest::qWaitFor([&]() { return weak_user.use_count() == 0; }));
  }
}

}; // namespace GarbageCollection
