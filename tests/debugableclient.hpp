#pragma once
#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "qtgql/bases/bases.hpp"
#include "qtgql/gqlwstransport/gqlwstransport.hpp"
using namespace qtgql;

QString get_server_address(const QString& suffix = "graphql");

struct DebugClientSettings {
  bool handle_ack = true;
  bool handle_pong = true;
  bool print_debug = false;
  gqlwstransport::GqlWsTransportClientSettings prod_settings = {
      .url = get_server_address()};
};

class DebugAbleClient : public gqlwstransport::GqlWsTransportClient {
  void onTextMessageReceived(const QString& raw_message);

 public:
  bool m_pong_received = false;
  DebugClientSettings m_settings;
  std::optional<gqlwstransport::GqlWsTrnsMsgWithID> m_current_message;

  DebugAbleClient(DebugClientSettings settings = DebugClientSettings())
      : GqlWsTransportClient(settings.prod_settings), m_settings{settings} {};
  const void wait_for_valid() {
    if (!QTest::qWaitFor([&]() { return gql_is_valid(); }, 1000)) {
      throw "Client could not connect to the GraphQL server";
    }
  }
  bool is_reconnect_timer_active() { return m_reconnect_timer->isActive(); }
  bool has_handler(const std::shared_ptr<bases::HandlerABC>& handler);

  static DebugAbleClient* from_environment(
      std::shared_ptr<bases::Environment> env) {
    return dynamic_cast<DebugAbleClient*>(env->get_network_layer());
  }
};

std::shared_ptr<DebugAbleClient> get_valid_client();

namespace test_utils {
void wait_for_completion(
    const std::shared_ptr<gqlwstransport::OperationHandlerABC> handler);
class QCleanerObject : public QObject {};

struct CompleteSpy {
  QSignalSpy* about_to;
  QSignalSpy* after;
  explicit CompleteSpy(QSignalSpy* about, QSignalSpy* _after)
      : about_to{about}, after{_after} {
    REQUIRE(about->isEmpty());
    REQUIRE(after->isEmpty());
  }

  void validate() {
    REQUIRE(!about_to->isEmpty());
    REQUIRE(!after->isEmpty());
  }
};

}  // namespace test_utils
