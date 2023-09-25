#include "gen/CreatePost.hpp"
#include "gen/UpdatePostContent.hpp"
#include "testframework.hpp"
#include "testutils.hpp"
#include <QSignalSpy>

namespace InputTypeOperationVariable {
using namespace qtgql;

auto ENV_NAME = std::string("InputTypeOperationVariable");
auto SCHEMA_ADDR = test_utils::get_server_address(QString::fromStdString(ENV_NAME));

TEST_CASE("InputTypeOperationVariable") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, test_utils::DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  auto create_post = createpost::CreatePost::shared();
  QString old_post_content("this is a great post about elephants");
  create_post->set_variables(
      {CreatePostInput::create(old_post_content, "Post header")});
  create_post->fetch();
  test_utils::wait_for_completion(create_post);
  auto post = create_post->data()->get_createPost();
  SECTION("test deserialize") {
    REQUIRE(post->get_header() == "Post header");
    REQUIRE(post->get_content() == old_post_content);
  };
  SECTION("test update") {
    auto update_post = updatepostcontent::UpdatePostContent::shared();
    QString new_content("This is a great post about dogs");
    update_post->set_variables(
        {ModifyPostContentInput::create(post->get_id(), new_content)});
    test_utils::SignalCatcher catcher({.source_obj = post, .only = "content"});
    update_post->fetch();
    REQUIRE(catcher.wait());
    test_utils::wait_for_completion(update_post);
    REQUIRE(post->get_content() == new_content);
  };
}

}; // namespace InputTypeOperationVariable
