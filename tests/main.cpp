#define DOCTEST_CONFIG_IMPLEMENT
#include "main.hpp"
#include <QGuiApplication>
#include <QTest>
#include <QTimer>
#include "testframework.hpp"


int main(int argc, char **argv) {
    doctest::Context context;
    context.applyCommandLine(argc, argv);
    context.setOption("no-breaks", true);
    auto app = QGuiApplication::instance();
      if (!app) {
        auto app = new QGuiApplication(argc, argv);
      }
      const Main &main = Main::getInstance();
        int test_exit_code = context.run(); // run

        if(context.shouldExit()) // important - query flags (and --exit) rely on the user doing this
            return test_exit_code;

    auto ret = app->exec();
      delete app;
      return test_exit_code + ret;
}
