#pragma once
#include <catch2/catch_test_macros.hpp>

#include <QSignalSpy>
#include <QTest>

#include <QQmlEngine>
#include <QQuickItem>
#include <QQuickView>

#include <filesystem>
#include <memory>

#include "qtgql/bases/bases.hpp"
#include "qtgql/gqltransportws/gqltransportws.hpp"

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
  QQuickView *qquick_view;
  QmlBot() {
    qquick_view = new QQuickView();
    auto qmltester = fs::path(__FILE__).parent_path() / "qmltester.qml";
    qquick_view->setSource(QUrl{qmltester.c_str()});
    auto errors = qquick_view->errors();
    if (!errors.empty()) {
      qDebug() << errors;
      throw "errors during qml load";
    }
    qquick_view->show();
  }

  template <typename T> T find(const QString &objectName) {
    return qquick_view->findChild<T>(objectName);
  };

  QQuickItem *loader() { return find<QQuickItem *>("contentloader"); };

  QQuickItem *load(const fs::path &path) {
    loader()->setProperty("source", path.c_str());
    assert_m((loader()->property("status").toInt() == 1),
             "could not load component");
    auto ret = loader()->findChildren<QQuickItem *>()[0];
    return ret;
  }

  [[nodiscard]] QQmlEngine *engine() const { return qquick_view->engine(); }

  ~QmlBot() {
    qquick_view->close();
    delete qquick_view;
  }
};

}; // namespace test_utils
