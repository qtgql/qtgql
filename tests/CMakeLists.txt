find_package(Qt6 REQUIRED COMPONENTS Test Core Network)
find_package(Catch2 REQUIRED COMPONENTS Catch2)
include(Catch)
find_package(Qt6 REQUIRED COMPONENTS Test Core Network)
set(TESTS_TARGET "test_qtgql")
file(GLOB_RECURSE TEST_SRCS ${PROJECT_SOURCE_DIR}/tests/test_*.cpp)

add_executable(${TESTS_TARGET} main.cpp ${TEST_SRCS} debugableclient.cpp)
include_directories(../tests)

add_subdirectory(test_codegen)
set_target_properties(${TESTS_TARGET} PROPERTIES AUTOMOC TRUE)
target_link_libraries(${TESTS_TARGET} PRIVATE Catch2::Catch2)
target_link_libraries(${TESTS_TARGET} PRIVATE Qt6::Core Qt6::Test Qt6::Network)
target_link_libraries(${TESTS_TARGET} PRIVATE qtgql)

catch_discover_tests(${TESTS_TARGET})
