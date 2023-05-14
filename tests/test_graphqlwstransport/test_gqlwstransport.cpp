#include <QTest>
#include <catch2/catch_test_macros.hpp>
#include <gqlwstransport.hpp>
#include <qtgqlenvironment.hpp>

QString get_server_address() {
  auto env_addr = std::getenv("SCHEMAS_SERVER_ADDR");
  if (env_addr) {
    return QString::fromUtf8(env_addr);
  }
  return "ws://localhost:9000/graphql";
}
struct DebugClientSettings {
  bool handle_ack = true;
  bool handle_pong = true;
  qtgql::GqlWsTransportClientSettings prod_settings = {
      .url = get_server_address()};
};

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

 public:
  bool m_pong_received = false;
  DebugClientSettings m_settings;
  DebugAbleClient(const DebugClientSettings &settings = {})
      : GqlWsTransportClient(settings.prod_settings), m_settings{settings} {}

  void wait_for_valid() {
    if (!QTest::qWaitFor([&]() { return gql_is_valid(); }, 1000)) {
      throw "Client could not connect to the GraphQL server";
    }
  }
  bool is_reconnect_timer_active() { return m_reconnect_timer->isActive(); }
  bool has_handler(const std::shared_ptr<qtgql::QtGqlHandlerABC> &handler) {
    return m_handlers.contains(handler->operation_id());
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

struct DefaultHandler : public qtgql::QtGqlHandlerABC {
  qtgql::GqlWsTrnsMsgWithID m_message;
  DefaultHandler(const QString &query = get_subscription_str())
      : m_message{qtgql::GqlWsTrnsMsgWithID(qtgql::OperationPayload(query))} {};

  QJsonArray m_errors;
  QJsonObject m_data;
  bool m_completed = false;
  const QUuid &operation_id() const override { return m_message.op_id; }
  void on_next(const QJsonObject &message) override {
    // here we copy the message though generally user wouldn't do this as it
    // would just use the reference to initialize some data
    m_data = message["data"].toObject();
  }

  void on_error(const QJsonArray &errors) override { m_errors = errors; }
  void on_completed() override { m_completed = true; }

  const qtgql::HashAbleABC &message() override { return m_message; }
  bool wait_for_completed() const {
    return QTest::qWaitFor([&]() -> bool { return m_completed; }, 1500);
  }

  bool count_eq_9() {
    if (m_data.value("count").isDouble()) {
      auto ret = m_data.value("count").toInt();
      return ret == 9;
    }
    return false;
  }
};

TEST_CASE("get operation name", "[gqlwstransport][ws-client]") {
  const QString operation_name = "SampleOperation";
  auto res_op_name =
      qtgql::get_operation_name("query SampleOperation {field1 field2}");
  REQUIRE(res_op_name);
  REQUIRE(res_op_name.value() == operation_name);
};

TEST_CASE("If ws not valid gql_valid=false", "[gqlwstransport][ws-client]") {
  auto client = get_valid_client();
  REQUIRE(QTest::qWaitFor([&]() { return client->gql_is_valid(); }, 1000));
  client->close();

  REQUIRE(QTest::qWaitFor([&]() -> bool { return !client->is_valid(); }, 700));
  REQUIRE(
      QTest::qWaitFor([&]() -> bool { return !client->gql_is_valid(); }, 700));
}

TEST_CASE("If ack not received - gql is not valid",
          "[gqlwstransport][ws-client]") {
  auto client = DebugAbleClient({.handle_ack = false});
  REQUIRE(QTest::qWaitFor([&]() { return client.is_valid(); }, 1000));
  std::ignore =
      QTest::qWaitFor([&]() -> bool { return client.gql_is_valid(); }, 200);
  REQUIRE(!client.gql_is_valid());
}

TEST_CASE("Connection init is sent and receives ack",
          "[gqlwstransport][ws-client]") {
  auto client = DebugAbleClient();
  auto success = QTest::qWaitFor([&]() { return client.gql_is_valid(); }, 1000);
  REQUIRE(success);
}

TEST_CASE("Send ping receive pong", "[gqlwstransport][ws-client]") {
  auto client = DebugAbleClient();
  REQUIRE(QTest::qWaitFor([&]() { return client.gql_is_valid(); }, 1000));
  auto success =
      QTest::qWaitFor([&]() { return client.m_pong_received; }, 1000);
  REQUIRE(success);
}

TEST_CASE("Subscribe to data (next message)", "[gqlwstransport][ws-client]") {
  auto client = get_valid_client();
  auto handler = std::make_shared<DefaultHandler>();
  auto serialized = handler->message().serialize();
  client->execute(handler);
  REQUIRE(
      QTest::qWaitFor([&]() -> bool { return handler->count_eq_9(); }, 1500));
}

TEST_CASE("execute via environment", "[gqlwstransport]") {
  auto env = new qtgql::QtGqlEnvironment("Sample env",
                                         std::make_unique<DebugAbleClient>());
  auto handler = std::make_shared<DefaultHandler>();
  env->execute(handler);
  handler->wait_for_completed();
}

TEST_CASE("Subscribe get complete message on complete",
          "[gqlwstransport][ws-client]") {
  auto client = get_valid_client();
  auto handler = std::make_shared<DefaultHandler>(get_subscription_str());
  REQUIRE(!handler->m_completed);
  client->execute(handler);
  REQUIRE(handler->wait_for_completed());
}

TEST_CASE("Ping timeout close connection", "[gqlwstransport][ws-client]") {
  auto client = DebugAbleClient(
      {.handle_pong = false,
       .prod_settings = {.url = get_server_address(), .ping_timeout = 500}});
  client.wait_for_valid();
  REQUIRE(QTest::qWaitFor([&]() -> bool { return !client.is_valid(); }, 700));
}

TEST_CASE("wont reconnect if reconnect is false",
          "[gqlwstransport][ws-client]") {
  auto client = DebugAbleClient({.prod_settings = {.url = get_server_address(),
                                                   .auto_reconnect = false}});
  client.wait_for_valid();
  client.close();
  REQUIRE(QTest::qWaitFor([&]() -> bool { return !client.is_valid(); }, 700));
}

TEST_CASE("Reconnection tests", "[gqlwstransport][ws-client]") {
  auto client = DebugAbleClient(
      {.prod_settings = {.url = get_server_address(), .auto_reconnect = true}});
  client.wait_for_valid();
  client.close();
  SECTION("reconnect on disconnected") {
    REQUIRE(
        QTest::qWaitFor([&]() -> bool { return client.gql_is_valid(); }, 700));
  }

  SECTION("reconnect timer won't call connection init again after reconnect") {
    REQUIRE(client.is_reconnect_timer_active());
    REQUIRE(
        QTest::qWaitFor([&]() -> bool { return client.gql_is_valid(); }, 700));
    REQUIRE(!client.is_reconnect_timer_active());
  }
}

TEST_CASE("client can have headers and and authorize",
          "[gqlwstransport][ws-client]") {
  QString expected_ret = "The resolver will return this";
  auto authorized_client = DebugAbleClient(
      {.prod_settings = {.url = get_server_address(),
                         .headers = {{"Authorization", expected_ret}}}});
  authorized_client.wait_for_valid();
  auto handler =
      std::make_shared<DefaultHandler>("query MyQuery {isAuthenticated}");
  authorized_client.execute(handler);
  REQUIRE(handler->wait_for_completed());
  REQUIRE(handler->m_data["isAuthenticated"] == expected_ret);
}

TEST_CASE("Handlers tests", "[gqlwstransport][handlers]") {
  auto client = get_valid_client();
  auto sub1 = std::make_shared<DefaultHandler>();
  auto sub2 = std::make_shared<DefaultHandler>();
  REQUIRE(sub1->operation_id() != sub2->operation_id());

  SECTION("executing handlers adds them to handlers map") {
    client->execute(sub1);
    client->execute(sub2);
    REQUIRE(bool(client->has_handler(sub1) && client->has_handler(sub2)));
  }

  SECTION("handler called on gql_next") {
    REQUIRE(sub1->m_data.empty());
    client->execute(sub1);
    REQUIRE(QTest::qWaitFor([&]() -> bool { return sub1->count_eq_9(); }));
  }
  SECTION("handler called on completed") {
    REQUIRE(!sub1->m_completed);
    client->execute(sub1);
    std::ignore = QTest::qWaitFor([&]() -> bool { return sub1->count_eq_9(); });
    REQUIRE(sub1->m_completed);
  }
  SECTION("handler completed pops out of handlers vector") {
    client->execute(sub1);
    REQUIRE(client->has_handler(sub1));
    REQUIRE(sub1->wait_for_completed());
    REQUIRE(!client->has_handler(sub1));
  }

  SECTION("if client is not connected pends the message to later") {
    client->close();
    REQUIRE(!client->is_valid());
    REQUIRE(!sub1->m_completed);
    client->execute(sub1);
    client->reconnect();
    REQUIRE(sub1->wait_for_completed());
  }

  SECTION("gql operation error passes error to operation handler") {
    auto sub_with_error =
        std::make_shared<DefaultHandler>(get_subscription_str(true));
    client->execute(sub_with_error);
    REQUIRE(QTest::qWaitFor(
        [&]() -> bool { return !sub_with_error->m_errors.isEmpty(); }));
    REQUIRE(
        sub_with_error->m_errors[0].toObject().value("message").toString() ==
        "Test Gql Error");
  }
}
TEST_CASE("Mutation and Query operations compatibility",
          "[gqlwstransport][handlers]") {
  auto client = get_valid_client();
  SECTION("mutation") {
    auto mutation_handler = std::make_shared<DefaultHandler>(
        "mutation TestMutation{pseudoMutation}");
    client->execute(mutation_handler);
    mutation_handler->wait_for_completed();
    bool is_bool = mutation_handler->m_data["pseudoMutation"].isBool();
    REQUIRE(is_bool);
    REQUIRE(mutation_handler->m_data["pseudoMutation"].toBool());
  }

  SECTION("query") {
    auto query_handler =
        std::make_shared<DefaultHandler>("query TestQuery{hello}");
    client->execute(query_handler);
    query_handler->wait_for_completed();
    REQUIRE(query_handler->m_data["hello"].toString() == "world");
  }
}

TEST_CASE("Test variables", "[gqlwstransport][handlers]") {
  auto client = get_valid_client();
  auto sub1 = std::make_shared<DefaultHandler>(
      QString("subscription Sub1($target: Int!, $raiseOn5: Boolean = false) {\n"
              "  count(target: $target, raiseOn5: $raiseOn5)\n"
              "}"));

  sub1->m_message.set_variables({{"target", 2}});
  client->wait_for_valid();
  client->execute(sub1);
  sub1->wait_for_completed();
  REQUIRE(sub1->m_data.value("count").toInt() == 1);
}
