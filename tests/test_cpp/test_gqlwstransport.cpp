#include <QTest>
#include <catch2/catch_test_macros.hpp>
#include <gqltransport.hpp>

#include "main.hpp"

class DebugAbleClient : public GqlWsTransportClient {
  void onTextMessageReceived(const QString &message) {
    auto raw_data = QJsonDocument::fromJson(message.toUtf8());
    GqlWsTransportClient::onTextMessageReceived(message);
    if (raw_data.isObject()) {
      auto data = raw_data.object();
      if (data.contains("id")) {
        // Any that contains ID is directed to a single handler.
        auto message = GqlWsTrnsMsgWithID(data);
        auto message_type = message.type;
      } else {
        auto message = BaseGqlWsTrnsMsg(data);
        auto message_type = message.type;
        if (message_type == PROTOCOL::PONG) {
          m_pong_received = true;
        }
      }
    }
    GqlWsTransportClient::onTextMessageReceived(message);
  }

 public:
  bool m_pong_received = false;

  DebugAbleClient(QString url) : GqlWsTransportClient(url) {}
};

static QString addr = "ws://localhost:9000/graphql";

TEST_CASE("get operation name", "[single-file]") {
  const QString operation_name = " SampleOperation";
  auto res_op_name =
      get_operation_name("query SampleOperation {field1 field2}");
  REQUIRE(res_op_name.value() == operation_name);
};

TEST_CASE("Connection init is sent and receives ack", "[single-file]") {
  auto client = GqlWsTransportClient(addr);
  auto success = QTest::qWaitFor([&]() { return client.gql_is_valid(); }, 1000);
  REQUIRE(success);
}

TEST_CASE("Send ping receive pong", "[single-file]") {
  auto client = DebugAbleClient(addr);
  REQUIRE(QTest::qWaitFor([&]() { return client.gql_is_valid(); }, 1000));
  auto success =
      QTest::qWaitFor([&]() { return client.m_pong_received; }, 1000);
  REQUIRE(success);
}
