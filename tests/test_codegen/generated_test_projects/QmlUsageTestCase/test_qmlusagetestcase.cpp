#include "testutils.hpp"
#include <QQmlApplicationEngine>
#include <QSignalSpy>
#include <catch2/catch_test_macros.hpp>
#include <filesystem>
namespace fs = std::filesystem;

namespace QmlUsageTestCase {
using namespace qtgql;

auto ENV_NAME = QString("QmlUsageTestCase");

auto SCHEMA_ADDR = get_server_address("46038122");

TEST_CASE("QmlUsageTestCase", "[generated-testcase]") {
  auto env = test_utils::get_or_create_env(
      ENV_NAME, DebugClientSettings{.prod_settings = {.url = SCHEMA_ADDR}});
  QQmlApplicationEngine engine;
  auto main_qml = fs::path(__FILE__).parent_path() / "qmlusagetestcase.qml";
  auto bot = test_utils::QmlBot();
  auto res = bot.load(main_qml);
  REQUIRE(res->objectName().toStdString() == "foobar");
  REQUIRE(QTest::qWaitFor([&] { return res->property("success").toBool(); }));
}
}; // namespace QmlUsageTestCase
