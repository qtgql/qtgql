#pragma once
#include <catch2/catch_test_macros.hpp>

#include <QSignalSpy>
#include <QTest>

#include <QQmlEngine>
#include <QQuickItem>
#include <QQuickView>

#include <filesystem>

#include "qtgql/bases/bases.hpp"
#include "qtgql/gqlwstransport/gqlwstransport.hpp"

using namespace qtgql;
namespace fs = std::filesystem;

#define assert_m(cond, msg)                                                    \
  if (!cond) {                                                                 \
    qDebug() << msg;                                                           \
  }                                                                            \
  assert(cond);

QString get_server_address(const QString &suffix = "graphql");

struct DebugClientSettings {
  bool handle_ack = true;
  bool handle_pong = true;
  bool print_debug = false;
  gqlwstransport::GqlWsTransportClientSettings prod_settings = {
      .url = get_server_address()};
};

class DebugAbleClient : public gqlwstransport::GqlWsTransportClient {
  void onTextMessageReceived(const QString &raw_message);

public:
  bool m_pong_received = false;
  DebugClientSettings m_settings;
  QJsonObject m_current_message;

  DebugAbleClient(DebugClientSettings settings = DebugClientSettings())
      : GqlWsTransportClient(settings.prod_settings), m_settings{settings} {};
  const void wait_for_valid() {
    if (!QTest::qWaitFor([&]() { return gql_is_valid(); }, 1000)) {
      throw "Client could not connect to the GraphQL server";
    }
  }
  bool is_reconnect_timer_active() { return m_reconnect_timer->isActive(); }
  bool has_handler(const std::shared_ptr<bases::HandlerABC> &handler);

  static DebugAbleClient *
  from_environment(std::shared_ptr<bases::Environment> env) {
    return dynamic_cast<DebugAbleClient *>(env->get_network_layer());
  };
};

std::shared_ptr<DebugAbleClient> get_valid_client();

namespace test_utils {
using namespace std::chrono_literals;
void wait_for_completion(
    const std::shared_ptr<gqlwstransport::OperationHandlerABC> handler);
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
get_or_create_env(const QString &env_name, const DebugClientSettings &settings,
                  std::chrono::milliseconds cache_dur = 5s);

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
    auto ret = loader()->findChildren<QQuickItem *>()[0];
    return ret;
  }

  QQmlEngine *engine() const { return qquick_view->engine(); }

  ~QmlBot() {
    qquick_view->close();
    delete qquick_view;
  }
};
}; // namespace test_utils
