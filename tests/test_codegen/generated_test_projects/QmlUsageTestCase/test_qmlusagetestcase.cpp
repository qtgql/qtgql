#include "debugableclient.hpp"
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
  auto main_qml = fs::path(__FILE__).parent_path() / "main.qml";
  engine.load(QUrl{main_qml.c_str()});
  REQUIRE(QTest::qWaitFor([] { return false; }));
}

}; // namespace QmlUsageTestCase
