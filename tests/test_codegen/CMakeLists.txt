add_subdirectory(generated_test_projects/ScalarsTestCase/graphql/__generated__)
target_link_libraries(${TESTS_TARGET} PRIVATE generated::ScalarsTestCase)
add_subdirectory(
  generated_test_projects/NoIdOnQueryTestCase/graphql/__generated__)

target_link_libraries(${TESTS_TARGET} PRIVATE generated::NoIdOnQueryTestCase)
add_subdirectory(generated_test_projects/DateTimeTestCase/graphql/__generated__)
target_link_libraries(${TESTS_TARGET} PRIVATE generated::DateTimeTestCase)
add_subdirectory(generated_test_projects/DecimalTestCase/graphql/__generated__)
target_link_libraries(${TESTS_TARGET} PRIVATE generated::DecimalTestCase)
add_subdirectory(generated_test_projects/DateTestCase/graphql/__generated__)
target_link_libraries(${TESTS_TARGET} PRIVATE generated::DateTestCase)
add_subdirectory(
  generated_test_projects/TimeScalarTestCase/graphql/__generated__)
target_link_libraries(${TESTS_TARGET} PRIVATE generated::TimeScalarTestCase)
add_subdirectory(
  generated_test_projects/OptionalScalarsTestCase/graphql/__generated__)
target_link_libraries(${TESTS_TARGET}
                      PRIVATE generated::OptionalScalarsTestCase)
add_subdirectory(
  generated_test_projects/NestedObjectTestCase/graphql/__generated__)
target_link_libraries(${TESTS_TARGET} PRIVATE generated::NestedObjectTestCase)
add_subdirectory(
  generated_test_projects/OptionalNestedObjectTestCase/graphql/__generated__)
target_link_libraries(${TESTS_TARGET}
                      PRIVATE generated::OptionalNestedObjectTestCase)
add_subdirectory(
  generated_test_projects/ObjectWithListOfObjectTestCase/graphql/__generated__)
target_link_libraries(${TESTS_TARGET}
                      PRIVATE generated::ObjectWithListOfObjectTestCase)
add_subdirectory(generated_test_projects/EnumTestCase/graphql/__generated__)
target_link_libraries(${TESTS_TARGET} PRIVATE generated::EnumTestCase)
add_subdirectory(
  generated_test_projects/InterfaceTestCase/graphql/__generated__)
target_link_libraries(${TESTS_TARGET} PRIVATE generated::InterfaceTestCase)
