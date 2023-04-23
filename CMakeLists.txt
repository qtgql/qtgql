cmake_minimum_required(VERSION 3.22.1)

# --get poetry version--
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
execute_process(COMMAND poetry version OUTPUT_VARIABLE RAW_VER)
string(REPLACE "qtgql " "" RAW_VER ${RAW_VER})
string(STRIP ${RAW_VER} POETRY_VERSION)

project(
  qtgql
  VERSION ${POETRY_VERSION}
  LANGUAGES CXX)
set(QTGQL_VERBOSE TRUE)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Core Qml Quick WebSockets)

qt_standard_project_setup()

add_subdirectory(./qtgql/codegen/cpp/)
add_subdirectory(./qtgql/gqltransport_cpp)
# --options--
option(QTGQL_VERBOSE "display helpful build information" FALSE)
option(QTGQL_TESTING "Enable tests" FALSE)

if(QTGQL_VERBOSE)
  message(STATUS "qtgql version: " ${POETRY_VERSION})
endif()

# ───── LIBRARY TESTS ─────

if(QTGQL_TESTING)
  if(QTGQL_VERBOSE)
    message(STATUS "building tests")
  endif()
  include(CTest)
  add_subdirectory(test_cpp)
endif()

add_custom_target(
  tidy
  COMMAND run-clang-tidy -p ${CMAKE_BINARY_DIR}
  COMMENT "cpp linter")