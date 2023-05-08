include_directories(
  generated_test_projects/ScalarsTestCase/graphql/__generated__)
target_link_libraries(${TESTS_TARGET} PRIVATE __generated__::ScalarsTestCase)
