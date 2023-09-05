find_package(Qt6 REQUIRED COMPONENTS Test Core Network)
find_package(Catch2 REQUIRED COMPONENTS Catch2)
include(Catch)
find_package(Qt6 REQUIRED COMPONENTS Test Core Network)
set(TESTS_TARGET "test_qtgql")


add_executable(${TESTS_TARGET} main.cpp ${TEST_SRCS} testutils.cpp testutils.hpp
        test_customscalar.cpp
        test_networklayers/test_gqlwstransport.cpp
        test_networklayers/test_graphql_over_http.cpp
        test_networklayers/utils.hpp
        test_networklayers/test_subscription_router.cpp
)
include_directories(../tests)

add_subdirectory(gen)

message(STATUS "codegen collected tests:" ${CODEGEN_TEST_SOURCES})
target_sources(${TESTS_TARGET}
        PRIVATE
        ${CODEGEN_TEST_SOURCES}
)


set_target_properties(${TESTS_TARGET} PROPERTIES AUTOMOC TRUE)
target_link_libraries(${TESTS_TARGET} PUBLIC Catch2::Catch2)
target_link_libraries(${TESTS_TARGET} PRIVATE Qt6::Test)
target_link_libraries(${TESTS_TARGET} PUBLIC Qt6::Qml)
target_link_libraries(${TESTS_TARGET} PRIVATE qtgql)

if (NOT WIN32)
    catch_discover_tests(${TESTS_TARGET})
endif (NOT WIN32)
