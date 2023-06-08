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

add_library(${PROJECT_NAME})

target_sources(
        ${PROJECT_NAME}
        PRIVATE
        # bases
        include/qtgql/bases/detail/environment.cpp
        # gqlwstransport
        include/qtgql/gqlwstransport/detail/gqlwstransport.cpp
        include/qtgql/gqlwstransport/detail/operationhandler.cpp
        # customscalars
        include/qtgql/customscalars/detail/implementations.cpp
)
target_link_libraries(
        ${PROJECT_NAME}
        PUBLIC
        Qt6::Core
        Qt6::WebSockets
)


# header files get added via FILE_SET
# BASE_DIR should point to the same directory that is used as the
# target_include_directory, otherwise the install paths may be off.
target_sources(${PROJECT_NAME} PUBLIC FILE_SET HEADERS
        BASE_DIRS include
        FILES
        # interfaces
        include/qtgql/bases/bases.hpp
        include/qtgql/gqlwstransport/gqlwstransport.hpp
        include/qtgql/customscalars/customscalars.hpp
        # bases
        include/qtgql/bases/detail/objecttype.hpp
        include/qtgql/bases/detail/metadata.hpp
        include/qtgql/bases/detail/listmodel.hpp
        include/qtgql/bases/detail/networklayer.hpp
        include/qtgql/bases/detail/exceptions.hpp
        include/qtgql/bases/detail/constants.hpp
        include/qtgql/bases/detail/environment.hpp
        include/qtgql/bases/detail/macros.hpp
        # gqlwstransport
        include/qtgql/gqlwstransport/detail/operationhandler.cpp
        include/qtgql/gqlwstransport/detail/gqlwstransport.hpp
        include/qtgql/gqlwstransport/detail/operationhandler.hpp
        # customscalars
        include/qtgql/customscalars/detail/basecustomscalar.hpp
        include/qtgql/customscalars/detail/implementations.hpp
        # misc
        include/qtgql/utils.hpp
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
