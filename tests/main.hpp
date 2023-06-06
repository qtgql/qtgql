#pragma once
#include <QCoreApplication>
#include <QDir>
#include <QProcess>
#include <QSignalSpy>
#include <QTcpServer>

QString get_open_port();

class Main : public QObject {
  Q_OBJECT

  void on_server_proc_stdout_ready() {
    qDebug() << proc->readAllStandardOutput();
  }
  void on_server_proc_stderr_ready() {
    qDebug() << proc->readAllStandardError();
  }

public:
  QProcess *proc;
  QString server_address = "";
  ~Main(){};
  static Main &getInstance() {
    static Main inst;
    return inst;
  }

private:
  QProcess m_proc;
  explicit Main() : QObject(nullptr) {
    proc = new QProcess(this);

    auto dir = QDir(__FILE__);
    dir.cdUp();
    dir.cdUp();
    dir.cdUp();
    proc->setWorkingDirectory(dir.absolutePath());
    connect(proc, &QProcess::readyReadStandardOutput, this,
            &Main::on_server_proc_stdout_ready);
    connect(proc, &QProcess::readyReadStandardError, this,
            &Main::on_server_proc_stderr_ready);

    //    proc->start("poetry", {"run", "python", "-m", "aiohttp.web", "-P",
    //    get_open_port(),
    //                           "tests.scripts.tests_server:init_func"});

    // proc->start("poetry",
    //             {"run", "python", "-c", "from tests.scripts.tests_server
    //             import main; main(8000)"}, QProcess::OpenModeFlag::ReadOnly);
  }
};
