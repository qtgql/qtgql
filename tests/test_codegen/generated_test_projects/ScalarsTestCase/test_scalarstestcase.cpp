#pragma once
#include <QSignalSpy>
#include <QTest>
#include <catch2/catch_test_macros.hpp>

#include "graphql/__generated__/MainQuery.hpp"

TEST_CASE("ScalarsTestCase") {
  qtgql::QtGqlEnvironment::set_gql_env(
      std::make_shared<qtgql::QtGqlEnvironment>(
          "ScalarsTestCase", std::unique_ptr<qtgql::GqlWsTransportClient>(
                                 new qtgql::GqlWsTransportClient(
                                     {.url = {"127.0.0.1:9000/91874716"}}))));
  REQUIRE(false);
  auto mq = std::make_shared<mainquery::MainQuery>();
}
