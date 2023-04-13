set(QTGQL_RUNTIME_HEADERS
    ./include/bases.h
)

set(QTGQL_RUNTIME_SRCS
    ./runtime/bases.cpp
)


add_library(QTGQL_RUNTIME STATIC  ${QTGQL_RUNTIME_SRCS})
set_target_properties(QTGQL_RUNTIME PROPERTIES PUBLIC_HEADER ${QTGQL_RUNTIME_HEADERS})
add_library(${CMAKE_PROJECT_NAME}::runtime ALIAS QTGQL_RUNTIME)
target_link_libraries(QTGQL_RUNTIME PRIVATE Qt6::Qml Qt6::Quick Qt6::Core)
