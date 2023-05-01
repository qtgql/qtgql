#include <QTest>
#include <catch2/catch_test_macros.hpp>
#include <gqltransport.hpp>

QString get_server_address() {
  auto env_addr = std::getenv("SCHEMAS_SERVER_ADDR");
  if (env_addr) {
    return QString::fromUtf8(env_addr);
  }
  return "ws://localhost:9000/graphql";
}

class DebugAbleClient : public qtgql::GqlWsTransportClient {
  void onTextMessageReceived(const QString &message) {
    auto raw_data = QJsonDocument::fromJson(message.toUtf8());
    if (raw_data.isObject()) {
      auto data = raw_data.object();
      if (data.contains("id")) {
        // Any that contains ID is directed to a single handler.
        auto message = qtgql::GqlWsTrnsMsgWithID(data);
      } else {
        auto message = qtgql::BaseGqlWsTrnsMsg(data);
        auto message_type = message.type;
        if (message_type == qtgql::PROTOCOL::PONG) {
          m_pong_received = true;
          if (!handle_pong) {
            return;
          }
        } else if (message_type == qtgql::PROTOCOL::CONNECTION_ACK &&
                   !handle_ack) {
          return;
        }
      }
    }
    GqlWsTransportClient::onTextMessageReceived(message);
  }

 public:
  bool m_pong_received = false;
  bool handle_pong = true;
  bool handle_ack = true;
  DebugAbleClient(QString url = get_server_address(), QObject *parent = nullptr,
                  int ping_interval = 50000, int ping_timeout = 5000,
                  int reconnect_timeout = 3000, bool auto_reconnect = false)
      : GqlWsTransportClient(url, parent, ping_interval, ping_timeout,
                             auto_reconnect) {}

  void wait_for_valid() {
    if (!QTest::qWaitFor([&]() { return gql_is_valid(); }, 1000)) {
      throw "Client could not connect to the GraphQL server";
    }
  }
};

std::shared_ptr<DebugAbleClient> get_valid_client() {
  auto client = std::make_shared<DebugAbleClient>();
  client->wait_for_valid();
  return client;
}

QString get_subscription_str(bool raiseOn5 = false,
                             QString op_name = "defaultOpName",
                             int target = 10) {
  QString ro5 = raiseOn5 ? "true" : "false";
  return QString("subscription %1 {count(target: %2, raiseOn5: %3) }")
      .arg(op_name, QString::number(target), ro5);
}

class DefaultHandler : public qtgql::GqlWsHandlerABC {
 private:
  qtgql::GqlWsTrnsMsgWithID m_message;

 public:
  DefaultHandler(const QString &query)
      : m_message{qtgql::GqlWsTrnsMsgWithID(qtgql::OperationPayload(query))} {
    qDebug() << QJsonDocument(m_message.serialize()).toJson();
  }

  QJsonObject m_data;
  bool m_completed = false;
  void onData(const QJsonObject &message) {
    // here we copy the message though generally user wouldn't do this as it
    // would just use the reference to initialize some data
    m_data = message;
  }

  void onError(const QJsonObject &message) { qDebug() << message; }
  void onCompleted() { m_completed = true; }

  const qtgql::GqlWsTrnsMsgWithID message() { return m_message; }
  bool count_eq_9() {
    if (m_data.contains("data") && m_data.value("data").isObject()) {
      auto data = m_data.value("data").toObject();
      auto ret = data.value("count").toInt();
      return ret == 9;
    }
    return false;
  }
};

TEST_CASE("get operation name", "[gqlwstransport-client]") {
  const QString operation_name = "SampleOperation";
  auto res_op_name =
      qtgql::get_operation_name("query SampleOperation {field1 field2}");
  REQUIRE(res_op_name.value() == operation_name);
};

TEST_CASE("If ws not valid gql_valid=false", "[gqlwstransport-client]") {
  auto client = get_valid_client();
  REQUIRE(QTest::qWaitFor([&]() { return client->gql_is_valid(); }, 1000));
  client->close();

  REQUIRE(QTest::qWaitFor([&]() -> bool { return !client->is_valid(); }, 700));
  REQUIRE(
      QTest::qWaitFor([&]() -> bool { return !client->gql_is_valid(); }, 700));
}

TEST_CASE("If ack not received - gql is not valid", "[gqlwstransport-client]") {
  auto client = DebugAbleClient(get_server_address());
  client.handle_ack = false;
  REQUIRE(QTest::qWaitFor([&]() { return client.is_valid(); }, 1000));
  std::ignore =
      QTest::qWaitFor([&]() -> bool { return client.gql_is_valid(); }, 200);
  REQUIRE(!client.gql_is_valid());
}

TEST_CASE("Connection init is sent and receives ack",
          "[gqlwstransport-client]") {
  auto client = qtgql::GqlWsTransportClient(get_server_address());
  auto success = QTest::qWaitFor([&]() { return client.gql_is_valid(); }, 1000);
  REQUIRE(success);
}

TEST_CASE("Send ping receive pong", "[gqlwstransport-client]") {
  auto client = DebugAbleClient();
  REQUIRE(QTest::qWaitFor([&]() { return client.gql_is_valid(); }, 1000));
  auto success =
      QTest::qWaitFor([&]() { return client.m_pong_received; }, 1000);
  REQUIRE(success);
}

TEST_CASE("Subscribe to data (next message)", "[gqlwstransport-client]") {
  auto client = get_valid_client();
  auto handler = std::make_shared<DefaultHandler>(get_subscription_str());
  client->execute(handler);
  REQUIRE(
      QTest::qWaitFor([&]() -> bool { return handler->count_eq_9(); }, 1500));
}

TEST_CASE("Subscribe get complete message on complete",
          "[gqlwstransport-client]") {
  auto client = get_valid_client();
  auto handler = std::make_shared<DefaultHandler>(get_subscription_str());
  REQUIRE(!handler->m_completed);
  client->execute(handler);
  REQUIRE(
      QTest::qWaitFor([&]() -> bool { return handler->m_completed; }, 1500));
}

TEST_CASE("Ping timeout close connection", "[gqlwstransport-client]") {
  auto client = DebugAbleClient(get_server_address(), nullptr, 5000, 500);
  client.handle_pong = false;
  client.wait_for_valid();
  REQUIRE(QTest::qWaitFor([&]() -> bool { return !client.is_valid(); }, 700));
}
