#include "gen/MainQuery.hpp"
#include "gen/schema.hpp"
#include "testframework.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <memory>

namespace RecursiveInputObject {
using namespace qtgql;

auto ENV_NAME = std::string("RecursiveInputObject");
auto SCHEMA_ADDR = get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("RecursiveInputObject") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});

  SECTION("test deserialize") {
    auto mq = mainquery::MainQuery::shared();
    mq->set_variables(
        {RecursiveInput::create(RecursiveInput::create(std::nullopt, 2), 2)});
    mq->fetch();
    test_utils::wait_for_completion(mq);
    REQUIRE(mq->data()->get_depth() == 2);
  };
}
}; // namespace RecursiveInputObject
