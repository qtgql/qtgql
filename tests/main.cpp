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
  QTimer::singleShot(0,
          [&]{
              QGuiApplication::exit(context.run()); // run


  }
          );


  auto ret = QGuiApplication::exec();
  delete app;
  return ret;
}
