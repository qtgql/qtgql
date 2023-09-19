#include "utils.hpp"
#include <qtgql/bases/bases.hpp>

using namespace qtgql;
TEST_CASE("GraphQLTransportWS") {

  SECTION("get_operation_name") {
    QString operation_name = "SampleOperation";
    auto res_op_name =
        bases::get_operation_name("query SampleOperation {field1 field2}");
    REQUIRE(res_op_name);
    REQUIRE(res_op_name.value() == operation_name);
  };
  auto valid_client = get_valid_ws_client();

  SECTION("If ws not valid gql_valid=false") {
    REQUIRE(
        QTest::qWaitFor([&]() { return valid_client->gql_is_valid(); }, 1000));
    valid_client->close();

    REQUIRE(QTest::qWaitFor([&]() -> bool { return !valid_client->is_valid(); },
                            700));
    REQUIRE(QTest::qWaitFor(
        [&]() -> bool { return !valid_client->gql_is_valid(); }, 700));
  }

  SECTION("If ack not received - gql is not valid") {
    auto invalid_client = DebugAbleWsNetworkLayer(
        DebugClientSettings{.url = get_server_address(), .handle_ack = false});
    REQUIRE(QTest::qWaitFor([&]() { return invalid_client.is_valid(); }, 1000));
    std::ignore = QTest::qWaitFor(
        [&]() -> bool { return invalid_client.gql_is_valid(); }, 200);
    REQUIRE(!invalid_client.gql_is_valid());
  }

  SECTION("Connection init is sent and receives ack") {
    auto client = DebugAbleWsNetworkLayer({.url = get_server_address()});
    auto success =
        QTest::qWaitFor([&]() { return client.gql_is_valid(); }, 1000);
    REQUIRE(success);
  }

  SECTION("Send ping receive pong") {
    auto success =
        QTest::qWaitFor([&]() { return valid_client->m_pong_received; }, 1000);
    REQUIRE(success);
  }

  SECTION("Subscribe to data (next message)") {
    auto handler = std::make_shared<DebugHandler>(get_subscription_str());
    valid_client->execute(handler);
    REQUIRE(QTest::qWaitFor(
        [&]() -> bool { return count_eq_9(handler->m_data); }, 1500));
  }

  SECTION("execute via environment") {
    auto env = new bases::Environment(
        "Sample env",
        std::shared_ptr<DebugAbleWsNetworkLayer>(
            new DebugAbleWsNetworkLayer({.url = get_server_address()})));
    auto handler = std::make_shared<DebugHandler>(get_subscription_str());
    env->execute(handler);
    handler->wait_for_completed();
    delete env;
  }

  SECTION("Subscribe get complete message on complete") {
    auto handler = std::make_shared<DebugHandler>(get_subscription_str());
    REQUIRE(!handler->m_completed);
    valid_client->execute(handler);
    handler->wait_for_completed();
  }

  SECTION("Ping timeout close connection") {
    auto client = DebugAbleWsNetworkLayer(
        {.handle_pong = false,
         .prod_settings = {.url = get_server_address(), .ping_timeout = 500}});
    client.wait_for_valid();
    REQUIRE(QTest::qWaitFor([&]() -> bool { return !client.is_valid(); }, 700));
  }

  SECTION("wont reconnect if reconnect is false") {
    auto client =
        DebugAbleWsNetworkLayer({.prod_settings = {.url = get_server_address(),
                                                   .auto_reconnect = false}});
    client.wait_for_valid();
    client.close();
    REQUIRE(QTest::qWaitFor([&]() -> bool { return !client.is_valid(); }, 700));
  }

  SECTION("Reconnection tests") {
    auto client =
        DebugAbleWsNetworkLayer({.prod_settings = {.url = get_server_address(),
                                                   .auto_reconnect = true}});
    client.wait_for_valid();
    client.close();
    SECTION("reconnect on disconnected") {
      REQUIRE(QTest::qWaitFor([&]() -> bool { return client.gql_is_valid(); },
                              700));
    }

    SECTION(
        "reconnect timer won't call connection init again after reconnect") {
      REQUIRE(client.is_reconnect_timer_active());
      REQUIRE(QTest::qWaitFor([&]() -> bool { return client.gql_is_valid(); },
                              700));
      REQUIRE(!client.is_reconnect_timer_active());
    }
  }

  SECTION("valid_client can have headers and and authorize") {
    QString expected_ret = "The resolver will return this";
    auto authorized_client = DebugAbleWsNetworkLayer(
        {.prod_settings = {.url = get_server_address(),
                           .headers = {{"Authorization", expected_ret}}}});
    authorized_client.wait_for_valid();
    auto handler =
        std::make_shared<DebugHandler>("query MyQuery {isAuthenticated}");
    authorized_client.execute(handler);
    handler->wait_for_completed();
    REQUIRE(handler->m_data["isAuthenticated"].toString().toStdString() ==
            expected_ret.toStdString());
  }
  SECTION("Mutation and Query operations compatibility") {
    SECTION("mutation") {
      auto mutation_handler = std::make_shared<DebugHandler>(
          "mutation TestMutation{pseudoMutation}");
      valid_client->execute(mutation_handler);
      mutation_handler->wait_for_completed();
      bool is_bool = mutation_handler->m_data["pseudoMutation"].isBool();
      REQUIRE(is_bool);
      REQUIRE(mutation_handler->m_data["pseudoMutation"].toBool());
    }

    SECTION("query") {
      auto query_handler =
          std::make_shared<DebugHandler>("query TestQuery{hello}");
      valid_client->execute(query_handler);
      query_handler->wait_for_completed();
      REQUIRE(query_handler->m_data["hello"].toString() == "world");
    }
  }

  SECTION("Test variables") {
    auto client = get_valid_ws_client();
    auto sub1 = std::make_shared<DebugHandler>(QString(
        "subscription Sub1($target: Int!, $raiseOn5: Boolean = false) {\n"
        "  count(target: $target, raiseOn5: $raiseOn5)\n"
        "}"));

    sub1->m_message.set_variables({{"target", 2}});
    client->wait_for_valid();
    client->execute(sub1);
    sub1->wait_for_completed();
    REQUIRE(sub1->m_data.value("count").toInt() == 1);
  }
}

// NOTE: these tests could exist in any other network layer.
TEST_CASE("Operation handlers tests") {
  auto valid_client = get_valid_ws_client();
  SECTION("Handlers tests") {
    auto sub1 = std::make_shared<DebugHandler>(get_subscription_str());
    auto sub2 = std::make_shared<DebugHandler>(get_subscription_str());

    SECTION("executing handlers adds them to handlers map") {
      valid_client->execute(sub1);
      valid_client->execute(sub2);
      REQUIRE(bool(valid_client->has_handler(sub1) &&
                   valid_client->has_handler(sub2)));
    }

    SECTION("handler called on gql_next") {
      REQUIRE(sub1->m_data.empty());
      valid_client->execute(sub1);
      REQUIRE(
          QTest::qWaitFor([&]() -> bool { return count_eq_9(sub1->m_data); }));
    }
    SECTION("handler called on completed") {
      REQUIRE(!sub1->m_completed);
      valid_client->execute(sub1);
      std::ignore =
          QTest::qWaitFor([&]() -> bool { return count_eq_9(sub1->m_data); });
      REQUIRE(sub1->m_completed);
    }
    SECTION("handler completed pops out of handlers vector") {
      valid_client->execute(sub1);
      REQUIRE(valid_client->has_handler(sub1));
      sub1->wait_for_completed();
      REQUIRE(!valid_client->has_handler(sub1));
    }

    SECTION("if valid_client is not connected pends the message to later") {
      valid_client->close();
      REQUIRE(!valid_client->is_valid());
      REQUIRE(!sub1->m_completed);
      valid_client->execute(sub1);
      valid_client->reconnect();
      REQUIRE(QTest::qWaitFor([&]() { return valid_client->gql_is_valid(); }));
      sub1->wait_for_completed();
    }

    SECTION("gql operation error passes error to operation handler") {
      auto sub_with_error =
          std::make_shared<DebugHandler>(get_subscription_str(true));
      valid_client->execute(sub_with_error);
      REQUIRE(QTest::qWaitFor(
          [&]() -> bool { return !sub_with_error->m_errors.isEmpty(); }));
      REQUIRE(
          sub_with_error->m_errors[0].toObject().value("message").toString() ==
          "Test Gql Error");
    }
  }
}
