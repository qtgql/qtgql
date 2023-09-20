//#define DOCTEST_CONFIG_IMPLEMENT
#include "testframework.hpp"
#include <QGuiApplication>
#include <QTest>
#include <QTimer>

#include <catch2/catch_session.hpp>



int main(int argc, char **argv) {
//  doctest::Context context;
//  context.applyCommandLine(argc, argv);
//  context.setOption("no-breaks",
//                    true); // don't break in the debugger when assertions fail

  auto app = QGuiApplication(argc, argv);

  QTimer::singleShot(0,
          [&]{
              QGuiApplication::exit(Catch::Session().run(argc, argv)); // run


  }
          );


  return QGuiApplication::exec();
}
