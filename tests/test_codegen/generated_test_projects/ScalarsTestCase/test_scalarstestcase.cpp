#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "graphql/__generated__/MainQuery.hpp"

TEST_CASE("ScalarsTestCase") {
  auto client = new qtgql::GqlWsTransportClient(
      {.url = {"ws://localhost:9000/91874716"}});
  REQUIRE(QTest::qWaitFor([&]() -> bool { return client->is_valid(); }, 1500));

  qtgql::QtGqlEnvironment::set_gql_env(
      std::make_shared<qtgql::QtGqlEnvironment>(
          "ScalarsTestCase",
          std::unique_ptr<qtgql::GqlWsTransportClient>(client)));

  auto mq = std::make_shared<mainquery::MainQuery>();
  mq->fetch();
  REQUIRE(QTest::qWaitFor([&]() -> bool { return mq->completed(); }, 1500));

  delete client;
}
