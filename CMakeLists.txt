cmake_minimum_required(VERSION 3.25.0)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
execute_process(COMMAND poetry version OUTPUT_VARIABLE RAW_VER)
string(REPLACE "qtgql " "" RAW_VER ${RAW_VER})
string(STRIP ${RAW_VER} POETRY_VERSION)

project(
  qtgql
  VERSION ${POETRY_VERSION}
  LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(MSVC)
  set(CMAKE_CXX_FLAGS
      "${CMAKE_CXX_FLAGS} /std:c++20 /Zc:__cplusplus /permissive-")
endif()
find_package(Qt6 REQUIRED COMPONENTS Core Qml Quick WebSockets)

qt_standard_project_setup()
add_subdirectory(qtgql/gqlwstransport)
add_subdirectory(qtgql/bases)
add_subdirectory(qtgql/utils)

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
endif()

add_custom_target(
  tidy
  COMMAND run-clang-tidy -p ${CMAKE_BINARY_DIR}
  COMMENT "cpp linter")
