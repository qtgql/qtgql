#include "graphql/__generated__/getRndPost.hpp"
#include "testutils.hpp"
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>

namespace ListOfScalarTestCase {
using namespace qtgql;

auto ENV_NAME = QString("ListOfScalarTestCase");
auto SCHEMA_ADDR = get_server_address("ListOfScalarTestCase");

TEST_CASE("ListOfScalarTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto rnd_post = getrndpost::getRndPost::shared();

  SECTION("test deserialize") {
    rnd_post->fetch();
    test_utils::wait_for_completion(rnd_post);
    auto tags_model = rnd_post->data()->get_post()->get_tags();
    REQUIRE(tags_model->rowCount() > 0);
    for (const auto &tag : *tags_model) {
      REQUIRE(!tag.isEmpty());
    }
  };
  SECTION("test update") { REQUIRE(false); };
}

}; // namespace ListOfScalarTestCase
