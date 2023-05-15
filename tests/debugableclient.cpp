#include "debugableclient.hpp"

QString get_server_address(const QString &suffix) {
  auto env_addr = std::getenv("SCHEMAS_SERVER_ADDR");
  QString addr = "ws://localhost:9000/";
  if (env_addr) {
    auto addr = QString::fromUtf8(env_addr);
  }
  return addr + suffix;
}

std::shared_ptr<DebugAbleClient> get_valid_client() {
  auto client = std::make_shared<DebugAbleClient>();
  client->wait_for_valid();
  return client;
}

bool DebugAbleClient::has_handler(
    const std::shared_ptr<qtgql::QtGqlHandlerABC> &handler) {
  return m_handlers.contains(handler->operation_id());
}

void DebugAbleClient::onTextMessageReceived(const QString &message) {
  auto raw_data = QJsonDocument::fromJson(message.toUtf8());
  if (raw_data.isObject()) {
    auto data = raw_data.object();
    if (m_settings.print_debug) {
      qDebug() << data;
    }
    if (data.contains("id")) {
      // Any that contains ID is directed to a single handler.
      auto message = qtgql::GqlWsTrnsMsgWithID(data);
    } else {
      auto message = qtgql::BaseGqlWsTrnsMsg(data);
      auto message_type = message.type;
      if (message_type == qtgql::PROTOCOL::PONG) {
        m_pong_received = true;
        if (!m_settings.handle_pong) {
          return;
        }
      } else if (message_type == qtgql::PROTOCOL::CONNECTION_ACK &&
                 !m_settings.handle_ack) {
        return;
      }
    }
  }
  GqlWsTransportClient::onTextMessageReceived(message);
}
