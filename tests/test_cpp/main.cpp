#include "main.hpp"

#include <QCoreApplication>
#include <QTest>
#include <QTimer>
#include <catch2/catch_session.hpp>

int main(int argc, char** argv) {
  auto app = QCoreApplication::instance();
  if (!app) {
    auto app = new QCoreApplication(argc, argv);
  }
  const Main& main = Main::getInstance();

  // auto success = QTest::qWaitFor(
  //     [&]() { return main.server_address.isEmpty() ? false : true; }, 3000);
  // if (!success) {
  //   app->exit(-1);
  // }
  QTimer::singleShot(
      0, [app, argc, argv]() { app->exit(Catch::Session().run(argc, argv)); });
  return app->exec();
  delete app;
}

QString get_open_port() {
  QTcpServer a(nullptr);
  a.listen();
  auto port = a.serverPort();
  auto ret = QString::number(port);
  a.close();
  return ret;
}
