include(FetchContent)

FetchContent_Declare(
  Catch2
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG v3.3.2 # or a later release
)

FetchContent_MakeAvailable(Catch2)
include(Catch)
find_package(Qt6 REQUIRED COMPONENTS Test Core Network)
set(TESTS_TARGET "test_qtgql")
file(GLOB TEST_SRCS ${PROJECT_SOURCE_DIR}/tests/**/test_*.cpp)
add_executable(${TESTS_TARGET} main.cpp ${TEST_SRCS})
set_target_properties(${TESTS_TARGET} PROPERTIES AUTOMOC TRUE)

target_link_libraries(${TESTS_TARGET} PRIVATE Catch2::Catch2)
target_link_libraries(${TESTS_TARGET} PRIVATE Qt6::Core Qt6::Test Qt6::Network)
target_link_libraries(${TESTS_TARGET} PRIVATE qtgql::gqlwstransport
                                              qtgql::bases)

catch_discover_tests(${TESTS_TARGET})
