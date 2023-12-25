cmake_minimum_required(VERSION 3.22.0)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(QTGQL_VERSION 0.138.1)

project(
  qtgql
  VERSION ${QTGQL_VERSION}
  LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_INCLUDE_CURRENT_DIR ON)

if (WIN32)
  set(CMAKE_OBJECT_PATH_MAX 500)
endif ()
find_package(Qt6 REQUIRED COMPONENTS Core Qml Quick WebSockets)
qt_standard_project_setup()
set(WINDOWS_EXPORT_ALL_SYMBOLS ON)




file(GLOB_RECURSE QTGQL_SOURCES "src/*.cpp" "src/*.hpp")

file(GLOB_RECURSE QTGQL_HEADERS "src/*.hpp")

add_library(${PROJECT_NAME} SHARED ${QTGQL_SOURCES}
        src/qtgql/routers/detail/routers.cpp)
add_library(${PROJECT_NAME}::${PROJECT_NAME} ALIAS ${PROJECT_NAME})
target_compile_definitions(${PROJECT_NAME} PRIVATE QTGQL_CORE_LIB_SHARED_BUILD)

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
if(QTGQL_TEST_GEN OR QTGQL_TEST_CORE)
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
