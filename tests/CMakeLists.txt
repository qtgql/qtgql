find_package(Catch2 REQUIRED COMPONENTS Catch2)
include(Catch)
find_package(Qt6 REQUIRED COMPONENTS Test Core Network)
set(TESTS_TARGET "test_qtgql")
set(CMAKE_OBJECT_PATH_MAX 9999)

add_executable(${TESTS_TARGET}
        main.cpp
        ${TEST_SRCS}
        testutils.cpp testutils.hpp
        test_networklayers/utils.hpp
        test_networklayers/utils.cpp
        test_listmodel.cpp

        test_customscalar.cpp
        test_networklayers/test_gqltransportws.cpp
        test_networklayers/test_graphql_over_http.cpp

        test_networklayers/test_subscription_router.cpp
)
add_compile_definitions(TESTS_QML_DIR=${TESTS_QML_DIR} ${TESTS_TARGET})
include_directories(../tests)

add_subdirectory(gen)

target_sources(${TESTS_TARGET}
        PRIVATE
        ${CODEGEN_TEST_SOURCES}
)
target_compile_features(${TESTS_TARGET} PRIVATE cxx_std_17)
set_target_properties(${TESTS_TARGET} PROPERTIES AUTOMOC TRUE)
target_link_libraries(${TESTS_TARGET}
 PUBLIC
    Qt6::Test
    Qt6::Qml
    qtgql
    Catch2::Catch2
)

catch_discover_tests(${TESTS_TARGET}
        DL_PATHS ${QT_DL_LIBRARIES}
)
