include(FetchContent)

FetchContent_Declare(
  Catch2
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG v3.3.2 # or a later release
)

FetchContent_MakeAvailable(Catch2)
include(Catch)
find_package(Qt6 REQUIRED COMPONENTS Test Core Network)

add_executable(tests main.hpp main.cpp test_gqlwstransport.cpp)

target_link_libraries(tests PRIVATE Catch2::Catch2)
target_link_libraries(tests PRIVATE Qt6::Core Qt6::Test Qt6::Network)
target_link_libraries(tests PRIVATE qtgql)

catch_discover_tests(tests)
