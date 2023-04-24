#pragma once
#include <QCoreApplication>
#include <QDir>
#include <QProcess>
#include <QSignalSpy>
#include <QTcpServer>

int get_open_port();

class Main : public QObject {
  Q_OBJECT

  void on_server_proc_stdout_ready() {
    qDebug() << proc->readAllStandardOutput();
    m_ready = true;
  }
  void on_server_proc_stderr_ready() {
    qDebug() << proc->readAllStandardError();
  }
  bool m_ready = false;

 public:
  QProcess *proc;

  Main() : QObject(nullptr) {
    proc = new QProcess(this);
    auto port = get_open_port();
    proc->setArguments({
        "poetry",
        "run",
        "python",
        "-m",
        "aiohttp.web",
        "-H",
        "localhost",
        "-P",
        QString::number(port),
        "tests.mini_gql_server:init_func",
    });

    auto dir = QDir(__FILE__);
    dir.cdUp();
    dir.cdUp();
    dir.cdUp();
    proc->setWorkingDirectory(dir.absolutePath());
    connect(proc, &QProcess::finished, this,
            [this](int exitCode, QProcess::ExitStatus exitStatus) {
              qDebug() << "exitCode: " << exitCode
                       << "exitStatus: " << exitStatus;
            });
    connect(proc, &QProcess::readyReadStandardOutput, this,
            &Main::on_server_proc_stdout_ready);
    connect(proc, &QProcess::readyReadStandardError, this,
            &Main::on_server_proc_stderr_ready);
    proc->start();
  }
};
