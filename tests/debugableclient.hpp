#pragma once
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "qtgql/bases/bases.hpp"
#include "qtgql/gqlwstransport/gqlwstransport.hpp"
#include "qtgql/gqlwstransport/operationhandler.hpp"
using namespace qtgql;

QString get_server_address(const QString &suffix = "graphql");

struct DebugClientSettings {
  bool handle_ack = true;
  bool handle_pong = true;
  bool print_debug = false;
  GqlWsTransportClientSettings prod_settings = {.url = get_server_address()};
};

class DebugAbleClient : public GqlWsTransportClient {
  void onTextMessageReceived(const QString &raw_message);

 public:
  bool m_pong_received = false;
  DebugClientSettings m_settings;
  DebugAbleClient(DebugClientSettings settings = DebugClientSettings())
      : GqlWsTransportClient(settings.prod_settings), m_settings{settings} {};
  void wait_for_valid() {
    if (!QTest::qWaitFor([&]() { return gql_is_valid(); }, 1000)) {
      throw "Client could not connect to the GraphQL server";
    }
  }
  bool is_reconnect_timer_active() { return m_reconnect_timer->isActive(); }
  bool has_handler(const std::shared_ptr<bases::HandlerABC> &handler);
};

std::shared_ptr<DebugAbleClient> get_valid_client();

namespace test_utils {
void wait_for_completion(const std::shared_ptr<OperationHandlerABC> handler);
}
