#include "main.hpp"

#include <QGuiApplication>
#include <QTest>
#include <QTimer>
#include <catch2/catch_session.hpp>

int main(int argc, char **argv) {
  auto app = QGuiApplication::instance();
  if (!app) {
    auto app = new QGuiApplication(argc, argv);
  }
  const Main &main = Main::getInstance();

  QTimer::singleShot(
      0, [app, argc, argv]() { app->exit(Catch::Session().run(argc, argv)); });
  auto ret = app->exec();
  delete app;
  return ret;
}
