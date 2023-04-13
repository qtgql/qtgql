cmake_minimum_required(VERSION 3.22.1)

# --get poetry version--

execute_process(COMMAND poetry version OUTPUT_VARIABLE RAW_VER)
string(REPLACE "qtgql " "" RAW_VER ${RAW_VER})
string(STRIP ${RAW_VER} POETRY_VERSION)

project(qtgql VERSION ${POETRY_VERSION} LANGUAGES CXX)
set(QTGQL_VERBOSE TRUE)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(QTGQL_VERBOSE)
    message(STATUS "qtgql version: " ${POETRY_VERSION})
endif()

find_package(Qt6  REQUIRED COMPONENTS Core Qml Quick)


qt_standard_project_setup()





add_subdirectory(
  ./qtgql/codegen/cpp/
)


# ───── LIBRARY TESTS ─────

if(QOLM_ENABLE_TESTS)
  include(cmake/FetchGTest.cmake)
  enable_testing()
  add_subdirectory(cpp_tests)
endif()
