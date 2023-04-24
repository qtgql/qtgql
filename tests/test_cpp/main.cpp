#include "main.hpp"

#include <catch2/catch_session.hpp>

int get_open_port() {
  auto sock = QTcpServer();
  sock.listen();
  auto port = sock.serverPort();
  sock.close();
  return port;
}

int main(int argc, char** argv) {
  if (!QCoreApplication::instance()) {
    QCoreApplication app(argc, argv);
  }
  Main inst = Main();
  QSignalSpy spy(inst.proc, SIGNAL(readyReadStandardError()));
  QSignalSpy spy2(inst.proc, SIGNAL(readyReadStandardOutput()));
  return Catch::Session().run(argc, argv);
}
