#pragma once

#include <QSignalSpy>
#include <QTest>

#include <QQmlEngine>
#include <QQuickItem>
#include <QQuickView>

#include <filesystem>
#include <memory>

#include "qtgql/bases/bases.hpp"
#include "qtgql/gqltransportws/gqltransportws.hpp"
#include "testframework.hpp"

using namespace qtgql;
namespace fs = std::filesystem;

#define assert_m(cond, msg)                                                    \
  if (!cond) {                                                                 \
    qDebug() << msg;                                                           \
  }                                                                            \
  assert(cond);

QString get_server_address(const QString &suffix = "graphql",
                           const QString &prefix = "ws");

struct DebugClientSettings {
  QString url;
  bool handle_ack = true;
  bool handle_pong = true;
  bool print_debug = false;

  gqltransportws::GqlTransportWsClientSettings prod_settings = {
      .url = url, .auto_reconnect = true, .reconnect_timeout = 500};
};

class DebugAbleWsNetworkLayer : public gqltransportws::GqlTransportWs {
  void onTextMessageReceived(const QString &raw_message);

public:
  bool m_pong_received = false;
  DebugClientSettings m_settings;
  QJsonObject m_current_message;

  DebugAbleWsNetworkLayer(
      const DebugClientSettings &settings = DebugClientSettings())
      : gqltransportws::GqlTransportWs(settings.prod_settings),
        m_settings{settings} {};
  void wait_for_valid() {
    if (!QTest::qWaitFor([&]() { return gql_is_valid(); }, 1000)) {
      throw "Client could not connect to the GraphQL server";
    }
  }
  bool is_reconnect_timer_active() { return m_reconnect_timer->isActive(); }
  bool has_handler(const std::shared_ptr<bases::HandlerABC> &handler);

  static DebugAbleWsNetworkLayer *
  from_environment(std::shared_ptr<bases::Environment> env) {
    return dynamic_cast<DebugAbleWsNetworkLayer *>(env->get_network_layer());
  };
};

std::shared_ptr<DebugAbleWsNetworkLayer> get_valid_ws_client();

namespace test_utils {
using namespace std::chrono_literals;
inline QString get_http_server_addr(const QString &suffix) {
  return get_server_address(suffix, "http");
}
void wait_for_completion(
    const std::shared_ptr<bases::OperationHandlerABC> &handler);
class QCleanerObject : public QObject {};

struct ModelSignalSpy {
  QSignalSpy *about_to;
  QSignalSpy *after;
  explicit ModelSignalSpy(QSignalSpy *about, QSignalSpy *_after)
      : about_to{about}, after{_after} {
    REQUIRE(about->isEmpty());
    REQUIRE(after->isEmpty());
  }

  void validate() {
    REQUIRE(!about_to->isEmpty());
    REQUIRE(!after->isEmpty());
  }
};

struct SignalCatcherParams {
  const QObject *source_obj;
  const QSet<QString> &excludes = {};
  bool exclude_id = true;
  const std::optional<QString> &only = {};
};

std::shared_ptr<qtgql::bases::Environment>
get_or_create_env(const std::string &env_name,
                  const DebugClientSettings &settings,
                  std::chrono::milliseconds cache_dur = 5s);
void remove_env(const QString &env_name);

class SignalCatcher {
  std::list<std::pair<QSignalSpy *, QString>> m_spys = {};
  QSet<QString> m_excludes = {};

public:
  SignalCatcher(const SignalCatcherParams &params);

  [[nodiscard]] bool wait(int timeout = 1000);
};

struct QmlBot {
  std::unique_ptr<QQmlEngine> m_engine;
  QmlBot() {
    m_engine = std::make_unique<QQmlEngine>();
    // TODO: make this relative and add a note.
    m_engine->addImportPath(
        R"(C:\Users\temp\Desktop\omortie_qtgql\build\Debug\tests)");
    qDebug() << m_engine->importPathList();
  }

  template <typename T> T find(const QString &objectName) {
    return m_engine->findChild<T>(objectName);
  };

  QQuickItem *load(const fs::path &path) {
    assert_m(QFileInfo(path).exists(), "source qml file doesn't exists.");
    auto pathstring = path.string();
    auto qml_file = QFile(QFileInfo(path).absoluteFilePath());
    qml_file.open(QIODevice::ReadOnly | QIODevice::Text);
    auto qmlcontent = qml_file.readAll();

    assert_m(!qmlcontent.isEmpty(), "file is empty");
    QQmlComponent component(m_engine.get());
    component.setData(qmlcontent, {});
    auto loaded = QTest::qWaitFor(
        [&] { return component.status() == QQmlComponent::Ready; });
    assert_m(loaded, component.errors());
    auto obj = component.create();
    assert_m((obj != nullptr), "couldn't create component");
    QQuickWindow *win = qobject_cast<QQuickWindow *>(obj);
    assert_m((win != nullptr),
             "make user your root component is an window") auto ret =
        win->findChildren<QQuickItem *>()[0];
    return ret;
  }
};

}; // namespace test_utils
