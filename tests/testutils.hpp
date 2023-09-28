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

namespace fs = std::filesystem;

#define qtgql_assert_m(cond, msg)                                              \
  if (!cond) {                                                                 \
    qDebug() << msg;                                                           \
  }                                                                            \
  REQUIRE(cond);

namespace test_utils {
using namespace qtgql;

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
  void onTextMessageReceived(const QString &raw_message) override;

public:
  bool m_pong_received = false;
  DebugClientSettings m_settings;
  QJsonObject m_current_message;

  explicit DebugAbleWsNetworkLayer(
      const DebugClientSettings &settings = DebugClientSettings());
  void wait_for_valid();
  bool is_reconnect_timer_active() { return m_reconnect_timer->isActive(); }
  bool has_handler(const std::shared_ptr<bases::HandlerABC> &handler);

  static DebugAbleWsNetworkLayer *
  from_environment(const std::shared_ptr<bases::Environment> &env);
};

std::shared_ptr<DebugAbleWsNetworkLayer> get_valid_ws_client();

using namespace std::chrono_literals;
inline QString get_http_server_addr(const QString &suffix) {
  return get_server_address(suffix, "http");
}
void wait_for_completion(
    const std::shared_ptr<bases::OperationHandlerABC> &handler);
class QCleanerObject : public QObject {
public:
  using QObject::QObject;
  QCleanerObject() = delete;
};

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

#define QTGQL_STRINGIFY(x) #x
#define QTGQL_TOSTRING(x) QTGQL_STRINGIFY(x)
struct QmlBot {
  QQuickView *m_qquick_view;
  QmlBot() {
    m_qquick_view = new QQuickView();
#ifdef _WIN32
    auto additional_path =
        QDir(fs::path(QTGQL_TOSTRING(TESTS_QML_DIR))).absolutePath();
    additional_path.replace('/', '\\');
    if (!QDir(additional_path).exists())
      qDebug() << "additional qml path doesn't exist";
    m_qquick_view->engine()->addImportPath(additional_path);

#endif
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

  QQuickItem *root_loader() { return find<QQuickItem *>("rootLoader"); };

  QQuickItem *load(const fs::path &path) {
    auto source = QFileInfo(path);
    qtgql_assert_m(source.exists(),
                   "source qml file doesn't exists.") auto component =
        new QQmlComponent(m_qquick_view->engine(),
                          QUrl::fromLocalFile(source.absoluteFilePath()),
                          QQmlComponent::PreferSynchronous);

    QObject *object = component->create();
    m_qquick_view->rootObject()
        ->findChild<QQuickItem *>("rootLoader")
        ->setProperty("sourceComponent",
                      QVariant::fromValue(qobject_cast<QObject *>(component)));
    object->setParent(m_qquick_view->rootObject());
    auto errors = m_qquick_view->errors();

    if (!errors.empty()) {
      qDebug() << errors << m_qquick_view->errors();
      throw "errors during qml load";
    }
    auto ret = root_loader()->findChildren<QQuickItem *>()[0];
    return ret;
  }

  [[nodiscard]] QQmlEngine *engine() const { return m_qquick_view->engine(); }

  ~QmlBot() {
    m_qquick_view->close();
    delete m_qquick_view;
  }
};
[[maybe_unused]] std::shared_ptr<bases::Environment>
get_or_create_env(const std::string &env_name,
                  const DebugClientSettings &settings,
                  std::chrono::milliseconds cache_dur = 5s);
void remove_env(const QString &env_name);

struct SignalCatcherParams {
  const QObject *source_obj = nullptr;
  const QSet<QString> &excludes = {};
  bool exclude_id = true;
  const std::optional<QString> &only = {};
};

class SignalCatcher {
  std::list<std::pair<QSignalSpy *, QString>> m_spys = {};
  QSet<QString> m_excludes = {};

public:
  explicit SignalCatcher(const SignalCatcherParams &params);

  [[nodiscard]] bool wait(int timeout = 1000);
};
}; // namespace test_utils
