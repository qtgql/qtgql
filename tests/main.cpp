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

  QTimer::singleShot(
      0, [app, argc, argv]() { app->exit(Catch::Session().run(argc, argv)); });
  return app->exec();
}
