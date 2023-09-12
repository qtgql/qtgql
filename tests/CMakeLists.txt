find_package(Qt6 REQUIRED COMPONENTS Test Core Network)
find_package(doctest REQUIRED)
find_package(Qt6 REQUIRED COMPONENTS Test Core Network)
include(doctest)
set(TESTS_TARGET "test_qtgql")
set(CMAKE_OBJECT_PATH_MAX 9999)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

#
#add_library(${TESTS_TARGET}  ${TEST_SRCS} testutils.cpp testutils.hpp
#        test_customscalar.cpp
#        test_networklayers/test_gqlwstransport.cpp
#        test_networklayers/test_graphql_over_http.cpp
#        test_networklayers/utils.hpp
#        test_networklayers/test_subscription_router.cpp
#)
#include_directories(../tests)

#add_subdirectory(gen)

#target_sources(${TESTS_TARGET}
#        PRIVATE
#        ${CODEGEN_TEST_SOURCES}
#)
#target_compile_features(${TESTS_TARGET} PRIVATE cxx_std_17)

#set_target_properties(${TESTS_TARGET} PROPERTIES AUTOMOC TRUE)
#target_link_libraries(${TESTS_TARGET}
# PUBLIC
#    Qt6::Test
#    Qt6::Qml
#    Qt6::Quick
#    qtgql
#    doctest::doctest
#    )

message(FATAL_ERROR ${CMAKE_CXX_COMPILER} ${CMAKE_CXX_FLAGS})
add_executable(check
    check.cpp
    test_foobar.cpp
#        testutils.cpp testutils.hpp
)
target_link_libraries(
        check
        Qt6::Test
            Qt6::Qml
            Qt6::Quick
            qtgql
            doctest::doctest
)
#if (NOT WIN32)
    doctest_discover_tests(check)
#endif (NOT WIN32)
