set(SCHEMA_TARGET "DateTimeTestCase")
add_library(${SCHEMA_TARGET} "")
add_library(generated::${SCHEMA_TARGET} ALIAS ${SCHEMA_TARGET})
# cmake-lint: disable=C0301
target_sources(
  ${SCHEMA_TARGET}
  PUBLIC
    /home/nir/Desktop/tzv5hob/qtgql/tests/test_codegen/generated_test_projects/DateTimeTestCase/graphql/__generated__/schema.hpp
    /home/nir/Desktop/tzv5hob/qtgql/tests/test_codegen/generated_test_projects/DateTimeTestCase/graphql/__generated__/MainQuery.hpp
)
target_link_libraries(${SCHEMA_TARGET} PUBLIC Qt6::Core qtgql::gqlwstransport
                                              qtgql::bases qtgql)
target_include_directories(${SCHEMA_TARGET} PUBLIC ${CMAKE_CURRENT_LIST_DIR})
