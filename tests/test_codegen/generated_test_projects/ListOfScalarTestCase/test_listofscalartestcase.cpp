#include "graphql/__generated__/AddPostTag.hpp"
#include "graphql/__generated__/GetRndPost.hpp"
#include "graphql/__generated__/RemovePostTag.hpp"
#include "graphql/__generated__/ReplacePostTag.hpp"

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
  auto rnd_post = getrndpost::GetRndPost::shared();
  rnd_post->fetch();
  test_utils::wait_for_completion(rnd_post);
  SECTION("test deserialize") {

    auto tags_model = rnd_post->data()->get_post()->get_tags();
    REQUIRE(tags_model->rowCount() > 0);
    for (const auto &tag : *tags_model) {
      REQUIRE(!tag.isEmpty());
    }
  };
  SECTION("test update append") {
    auto add_tag_mut = addposttag::AddPostTag::shared();
    QString new_tag("foobar");
    add_tag_mut->set_variables(
        {.postID = rnd_post->data()->get_post()->get_id(), .tag = new_tag});
    add_tag_mut->fetch();
    test_utils::wait_for_completion(add_tag_mut);
    auto model = rnd_post->data()->get_post()->get_tags();
    auto last = model->last();
    REQUIRE(last.toStdString() == new_tag.toStdString());
  };

  SECTION("test update remove") {
    auto prev_ln = rnd_post->data()->get_post()->get_tags()->rowCount();
    auto remove_tag_mut = removeposttag::RemovePostTag::shared();
    remove_tag_mut->set_variables(
        {.postID = rnd_post->data()->get_post()->get_id(), .at = 2});
    remove_tag_mut->fetch();
    test_utils::wait_for_completion(remove_tag_mut);
    auto model = rnd_post->data()->get_post()->get_tags();
    REQUIRE(model->rowCount() < prev_ln);
  };
}

}; // namespace ListOfScalarTestCase
