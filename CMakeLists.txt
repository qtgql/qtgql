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
        PUBLIC
        include/qtgql/bases/bases.hpp
        include/qtgql/gqlwstransport/gqlwstransport.hpp
        include/qtgql/customscalars/customscalars.hpp
        PRIVATE
        # bases
        include/qtgql/bases/detail/environment.cpp
        include/qtgql/bases/detail/objecttype.hpp
        include/qtgql/bases/detail/metadata.hpp
        include/qtgql/bases/detail/listmodel.hpp
        include/qtgql/bases/detail/networklayer.hpp
        include/qtgql/bases/detail/exceptions.hpp
        include/qtgql/bases/detail/constants.hpp
        include/qtgql/bases/detail/environment.hpp
        # gqlwstransport
        include/qtgql/gqlwstransport/detail/gqlwstransport.cpp
        include/qtgql/gqlwstransport/detail/operationhandler.cpp
        include/qtgql/gqlwstransport/detail/gqlwstransport.hpp
        include/qtgql/gqlwstransport/detail/operationhandler.hpp
        # customscalars
        include/qtgql/customscalars/detail/basecustomscalar.hpp
        include/qtgql/customscalars/detail/implementations.hpp
        include/qtgql/customscalars/detail/implementations.cpp
)
target_link_libraries(
        ${PROJECT_NAME}
        PUBLIC
        Qt6::Core
        Qt6::WebSockets
)
target_include_directories(${PROJECT_NAME} PUBLIC include)

# --options--
option(QTGQL_VERBOSE "display helpful build information" true)
option(QTGQL_TESTING "Enable tests" FALSE)




# install
install(TARGETS ${PROJECT_NAME} EXPORT ${PROJECT_NAME}Targets
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
        )

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

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
