#include "debugableclient.hpp"
using namespace qtgql;

QString get_server_address(const QString &suffix) {
  auto env_addr = std::getenv("SCHEMAS_SERVER_ADDR");
  QString addr = "ws://localhost:9000/";
  if (env_addr) {
    addr = QString::fromUtf8(env_addr);
  }
  return addr + suffix;
}

std::shared_ptr<DebugAbleClient> get_valid_client() {
  auto client = std::make_shared<DebugAbleClient>();
  client->wait_for_valid();
  return client;
}

bool DebugAbleClient::has_handler(
    const std::shared_ptr<bases::HandlerABC> &handler) {
  return m_handlers.contains(handler->operation_id());
}

void DebugAbleClient::onTextMessageReceived(const QString &raw_message) {
  auto raw_data = QJsonDocument::fromJson(raw_message.toUtf8());
  if (raw_data.isObject()) {
    auto data = raw_data.object();
    if (m_settings.print_debug) {
      qDebug() << data;
    }
    if (data.contains("id")) {
      // Any that contains ID is directed to a single handler.
      auto message = gqlwstransport::GqlWsTrnsMsgWithID(data);
      if (message.type == qtgql::gqlwstransport::PROTOCOL::NEXT) {
        m_current_message = message.payload;
      } else if (message.type == qtgql::gqlwstransport::PROTOCOL::COMPLETE) {
        if (m_settings.print_debug) {
          qDebug() << "Completed";
        }
      }
    } else {
      auto message = gqlwstransport::BaseGqlWsTrnsMsg(data);
      auto message_type = message.type;
      if (message_type == gqlwstransport::PROTOCOL::PONG) {
        m_pong_received = true;
        if (!m_settings.handle_pong) {
          return;
        }
      } else if (message_type == gqlwstransport::PROTOCOL::CONNECTION_ACK &&
                 !m_settings.handle_ack) {
        return;
      }
    }
  }
  GqlWsTransportClient::onTextMessageReceived(raw_message);
}

namespace test_utils {
void wait_for_completion(
    const std::shared_ptr<qtgql::gqlwstransport::OperationHandlerABC>
        operation) {
  REQUIRE(
      QTest::qWaitFor([&]() -> bool { return operation->completed(); }, 1500));
}
std::shared_ptr<qtgql::bases::Environment> get_or_create_env(
    const QString &env_name, const DebugClientSettings &settings) {
  auto env = bases::Environment::get_gql_env(env_name);
  if (!env.has_value()) {
    auto env_ = std::make_shared<bases::Environment>(
        env_name, std::unique_ptr<qtgql::gqlwstransport::GqlWsTransportClient>(
                      new DebugAbleClient(settings)));
    bases::Environment::set_gql_env(env_);
    DebugAbleClient::from_environment(env_)->wait_for_valid();
    env = bases::Environment::get_gql_env(env_name);
  }
  return env.value();
};
}  // namespace test_utils
