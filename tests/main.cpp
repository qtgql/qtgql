#define DOCTEST_CONFIG_IMPLEMENT
#include "testframework.hpp"
#include <QGuiApplication>
#include <QTest>
#include <QTimer>

int main(int argc, char **argv) {
  doctest::Context context;
  context.applyCommandLine(argc, argv);
  context.setOption("no-breaks",
                    true); // don't break in the debugger when assertions fail

  auto app = QGuiApplication::instance();
  if (!app) {
    app = new QGuiApplication(argc, argv);
  }
  int res = context.run(); // run

  if (context.shouldExit()) // important - query flags (and --exit) rely on the
                            // user doing this
    return res;             // propagate the result of the tests

  auto ret = QGuiApplication::exec();
  delete app;
  return ret;
}
