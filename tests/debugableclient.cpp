#include "debugableclient.hpp"

QString get_server_address() {
  auto env_addr = std::getenv("SCHEMAS_SERVER_ADDR");
  if (env_addr) {
    return QString::fromUtf8(env_addr);
  }
  return "ws://localhost:9000/graphql";
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
