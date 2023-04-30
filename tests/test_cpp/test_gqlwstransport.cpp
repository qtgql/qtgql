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
    GqlWsTransportClient::onTextMessageReceived(message);
    if (raw_data.isObject()) {
      auto data = raw_data.object();
      if (data.contains("id")) {
        // Any that contains ID is directed to a single handler.
        auto message = qtgql::GqlWsTrnsMsgWithID(data);
        auto message_type = message.type;
      } else {
        auto message = qtgql::BaseGqlWsTrnsMsg(data);
        auto message_type = message.type;
        if (message_type == qtgql::PROTOCOL::PONG) {
          m_pong_received = true;
        }
      }
    }
    GqlWsTransportClient::onTextMessageReceived(message);
  }

 public:
  bool m_pong_received = false;

  DebugAbleClient(QString url = get_server_address())
      : GqlWsTransportClient(url) {}
};

std::shared_ptr<DebugAbleClient> get_valid_client() {
  auto client = std::make_shared<DebugAbleClient>();
  if (!QTest::qWaitFor([&]() { return client->gql_is_valid(); }, 1000)) {
    throw "Client could not connect to the GraphQL server";
  }
  return client;
}

TEST_CASE("get operation name", "[single-file]") {
  const QString operation_name = "SampleOperation";
  auto res_op_name =
      qtgql::get_operation_name("query SampleOperation {field1 field2}");
  REQUIRE(res_op_name.value() == operation_name);
};

TEST_CASE("Connection init is sent and receives ack", "[single-file]") {
  auto client = qtgql::GqlWsTransportClient(get_server_address());
  auto success = QTest::qWaitFor([&]() { return client.gql_is_valid(); }, 1000);
  REQUIRE(success);
}

TEST_CASE("Send ping receive pong", "[single-file]") {
  auto client = DebugAbleClient();
  REQUIRE(QTest::qWaitFor([&]() { return client.gql_is_valid(); }, 1000));
  auto success =
      QTest::qWaitFor([&]() { return client.m_pong_received; }, 1000);
  REQUIRE(success);
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

TEST_CASE("Subscribe to data (next message)", "[single-file]") {
  auto client = get_valid_client();
  auto handler = std::make_shared<DefaultHandler>(get_subscription_str());
  client->execute(handler);
  REQUIRE(
      QTest::qWaitFor([&]() -> bool { return handler->count_eq_9(); }, 1500));
}
