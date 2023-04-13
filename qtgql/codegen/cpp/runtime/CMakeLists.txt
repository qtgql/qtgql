set(QTGQL_RUNTIME_HEADERS
    ./bases.h
)

set(QTGQL_RUNTIME_SRCS
    ./bases.cpp
)


add_library(QTGQL_RUNTIME STATIC  ${QTGQL_RUNTIME_SRCS})
add_library(${CMAKE_PROJECT_NAME}::runtime ALIAS QTGQL_RUNTIME)
target_link_libraries(QTGQL_RUNTIME PRIVATE Qt6::Qml Qt6::Quick Qt6::Core)
