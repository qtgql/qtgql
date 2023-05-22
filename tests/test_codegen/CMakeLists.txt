add_subdirectory(generated_test_projects/ScalarsTestCase/graphql/__generated__)
target_link_libraries(${TESTS_TARGET} PRIVATE generated::ScalarsTestCase)
add_subdirectory(
  generated_test_projects/NoIdOnQueryTestCase/graphql/__generated__)

target_link_libraries(${TESTS_TARGET} PRIVATE generated::NoIdOnQueryTestCase)

target_link_libraries(${TESTS_TARGET} PRIVATE generated::DateTimeTestCase)
