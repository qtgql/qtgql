find_package(Qt6 REQUIRED COMPONENTS Test Core Network)
find_package(Catch2 REQUIRED COMPONENTS Catch2)
include(Catch)
set(TESTS_TARGET "test_qtgql")
set(CMAKE_OBJECT_PATH_MAX 9999)

add_library(utils_for_tests
        testutils.cpp testutils.hpp
        test_networklayers/utils.hpp
        test_networklayers/utils.cpp
)
target_link_libraries(utils_for_tests
        PUBLIC
        Qt6::Quick
        Qt6::Test
        Qt6::Qml
        qtgql
        Catch2::Catch2
)

add_executable(${TESTS_TARGET}
        main.cpp
        ${CODEGEN_TEST_SOURCES}
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
        utils_for_tests
)
if (QTGQL_SHOULD_TEST_CORE)

    add_executable(test_core
            main.cpp

            test_listmodel.cpp

            test_customscalar.cpp
            test_networklayers/test_gqltransportws.cpp
            test_networklayers/test_graphql_over_http.cpp

            test_networklayers/test_subscription_router.cpp
    )
    target_link_libraries(test_core
            PUBLIC
            Qt6::Test
            Qt6::Qml
            qtgql
            Catch2::Catch2
            utils_for_tests
    )
    catch_discover_tests(test_core
            DL_PATHS ${QT_DL_LIBRARIES}
    )
endif()

catch_discover_tests(${TESTS_TARGET}
        DL_PATHS ${QT_DL_LIBRARIES}
)
