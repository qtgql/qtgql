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
  QQuickView *m_qquick_view;
  QmlBot() {
    m_qquick_view = new QQuickView();
    auto qmltester =
        QFileInfo(fs::path(__FILE__).parent_path() / "qmltester.qml");
    m_qquick_view->setSource(QUrl::fromLocalFile(qmltester.absoluteFilePath()));
    auto loaded = QTest::qWaitFor(
        [this] { return this->m_qquick_view->status() == QQuickView::Ready; });
    auto errors = m_qquick_view->errors();
    if (!errors.empty() || !loaded) {
      qDebug() << errors;
      throw "errors during qml load";
    }
    m_qquick_view->show();
  }

  template <typename T> T find(const QString &objectName) {
    return m_qquick_view->findChild<T>(objectName);
  };

  QQuickItem *root_rect() { return find<QQuickItem *>("rootRect"); };

  QQuickItem *load(const fs::path &path) {
    auto source = QFileInfo(path);
    assert_m(source.exists(), "source qml file doesn't exists.")
        QQmlComponent component(m_qquick_view->engine(),
                                QUrl::fromLocalFile(source.absoluteFilePath()),
                                QQmlComponent::PreferSynchronous);
    if (!QTest::qWaitFor([&] { return component.isReady(); }))

      assert_m(false, component.errors());

    QObject *object = component.create();
    object->setParent(m_qquick_view->rootObject());
    auto errors = m_qquick_view->errors();

    if (!errors.empty()) {
      qDebug() << errors << m_qquick_view->errors();
      throw "errors during qml load";
    }
    auto ret = root_rect()->findChildren<QQuickItem *>()[0];
    return ret;
  }

  [[nodiscard]] QQmlEngine *engine() const { return m_qquick_view->engine(); }

  ~QmlBot() {
    m_qquick_view->close();
    delete m_qquick_view;
  }
};

}; // namespace test_utils
