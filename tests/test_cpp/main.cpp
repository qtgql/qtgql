#include "main.hpp"

#include <QTimer>
#include <catch2/catch_session.hpp>

int get_open_port() {
  auto sock = QTcpServer();
  sock.listen();
  auto port = sock.serverPort();
  sock.close();
  return port;
}

int main(int argc, char** argv) {
  auto app = QCoreApplication::instance();
  if (!app) {
    auto app = new QCoreApplication(argc, argv);
  }
  QTimer::singleShot(0, [&] { app->exit(Catch::Session().run(argc, argv)); });
  return app->exec();
}
