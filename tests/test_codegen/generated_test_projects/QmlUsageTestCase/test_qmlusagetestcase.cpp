#include "graphql/__generated__/FriendsListQuery.hpp"
#include "graphql/__generated__/RemoveFriend.hpp"
#include "testutils.hpp"
#include <QQmlApplicationEngine>
#include <catch2/catch_test_macros.hpp>
#include <filesystem>
namespace fs = std::filesystem;

namespace QmlUsageTestCase {
using namespace qtgql;

auto ENV_NAME = std::string("QmlUsageTestCase");

auto SCHEMA_ADDR = get_server_address("QmlUsageTestCase");

bool check_list_view_count(const QQuickItem *list_view, int expected) {

  return QTest::qWaitFor([&] {
    auto children_count = list_view->property("count").toInt();
    qDebug() << "children count" << children_count;
    qDebug() << "expected" << expected;
    return expected == children_count;
  });
}

TEST_CASE("QmlUsageTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  QQmlApplicationEngine engine;
  auto bot = test_utils::QmlBot();

  SECTION("test on_completed hook") {
    auto main_qml =
        fs::path(__FILE__).parent_path() / "testoncompletedhook.qml";

    auto root_qquickitem = bot.load(main_qml);

    REQUIRE(QTest::qWaitFor(
        [&] { return root_qquickitem->property("success").toBool(); }));
  }
  auto store_id = QUuid::createUuid().toString();
  auto friends_query = friendslistquery::FriendsListQuery::shared();
  friends_query->set_variables({store_id});
  friends_query->fetch();
  test_utils::wait_for_completion(friends_query);

  SECTION("test list view updates") {
    auto main_qml = fs::path(__FILE__).parent_path() / "testlistview.qml";
    auto root_qquickitem = bot.load(main_qml);
    root_qquickitem->setProperty("model",
                                 QVariant::fromValue(friends_query.get()));
    auto list_view = root_qquickitem->findChild<QQuickItem *>("friendsList");
    auto friends_model = friends_query->data()->get_friends();
    auto friends_count = friends_model->rowCount();
    auto last_friend_id = friends_model->last()->get_id();
    REQUIRE(check_list_view_count(list_view, friends_count));
    auto remove_friend_mut = removefriend::RemoveFriend::shared();
    remove_friend_mut->set_variables({store_id, last_friend_id});
    remove_friend_mut->fetch();
    test_utils::wait_for_completion(remove_friend_mut);
    friends_query->refetch();
    test_utils::wait_for_completion(friends_query);
    REQUIRE(check_list_view_count(list_view, friends_count - 1));
  }
}
}; // namespace QmlUsageTestCase
