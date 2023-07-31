cmake_minimum_required(VERSION 3.22.0)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(QTGQL_VERSION 0.130.8)

project(
  qtgql
  VERSION ${QTGQL_VERSION}
  LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(MSVC)
  set(CMAKE_CXX_FLAGS
      "${CMAKE_CXX_FLAGS} /std:c++20 /Zc:__cplusplus /permissive-")
endif()
find_package(Qt6 REQUIRED COMPONENTS Core Qml Quick WebSockets)
qt_standard_project_setup()




file(GLOB_RECURSE QTGQL_SOURCES "src/*.cpp" "src/*.hpp")

file(GLOB_RECURSE QTGQL_HEADERS "src/*.hpp")

add_library(${PROJECT_NAME} SHARED ${QTGQL_SOURCES})
add_library(${PROJECT_NAME}::${PROJECT_NAME} ALIAS ${PROJECT_NAME})

target_link_libraries(
        ${PROJECT_NAME}
        PUBLIC
        Qt6::Core
        Qt6::WebSockets
        Qt6::Network
)


# header files get added via FILE_SET
# BASE_DIR should point to the same directory that is used as the
# target_include_directory, otherwise the install paths may be off.
target_sources(${PROJECT_NAME} PUBLIC FILE_SET HEADERS
        BASE_DIRS src
        FILES
        ${QTGQL_HEADERS}
        )

# install with headers
install(TARGETS ${PROJECT_NAME} FILE_SET HEADERS)


# --options--
option(QTGQL_VERBOSE "display helpful build information" true)
option(QTGQL_TESTING "Enable tests" FALSE)


# ───── LIBRARY TESTS ─────

if(QTGQL_TESTING)
  if(QTGQL_VERBOSE)
    message(STATUS "building tests")
  endif()
  include(CTest)
  add_subdirectory(tests)
  add_custom_target(
    tidy
    COMMAND run-clang-tidy -p ${CMAKE_BINARY_DIR}
    COMMENT "cpp linter")
endif()
