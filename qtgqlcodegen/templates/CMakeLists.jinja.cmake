cmake_minimum_required(VERSION 3.20)
set(EnvTarget "👉 context.target_name 👈")
set(QTGQL_QML_PLUGIN_DIRECTORY 👉 context.config.qml_plugins_path 👈/GraphQL/${EnvTarget})

# add import path for Qt-Creator usage.
if (NOT ${CMAKE_BINARY_DIR}/qml IN_LIST QML_DIRS)
    list(APPEND QML_DIRS ${CMAKE_BINARY_DIR}/qml)
    set(QML_IMPORT_PATH "${QML_DIRS}" CACHE PATH "Qt Creator 10.1 extra qml import paths")
endif()

# Configure general compilation
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Core Quick Qml)

if(QT_VERSION VERSION_GREATER_EQUAL "6.3")
    qt_standard_project_setup()
else()
    set(CMAKE_AUTOMOC ON)
    set(CMAKE_AUTORCC ON)
    set(CMAKE_AUTOUIC ON)
endif()

# see https://doc.qt.io/qt-6/qt-cmake-policy-qtp0001.html
qt_policy(SET QTP0001 NEW)

add_library(${EnvTarget}schema
        schema.hpp
        )
target_link_libraries(${EnvTarget}schema
        PUBLIC
        Qt::Core
        qtgql::qtgql
        )

target_compile_definitions(${EnvTarget}schema PRIVATE 👉 context.config.shared_lib_export_definition 👈)
{% for operation in context.generation_output.operations -%}
qt_add_qml_module(${EnvTarget}👉 operation.name 👈
        URI GraphQL.${EnvTarget}.👉 operation.name 👈
        OUTPUT_DIRECTORY ${QTGQL_QML_PLUGIN_DIRECTORY}/👉 operation.name 👈
        SOURCES
        {% for filespec in operation.sources -%}
        👉 filespec.path.as_posix() 👈
        {% endfor -%}
        )

target_link_libraries(${EnvTarget}👉 operation.name 👈 PUBLIC
        Qt::CorePrivate
        Qt::QuickPrivate
        Qt::QmlPrivate
        ${EnvTarget}schema
        qtgql::qtgql
        )
target_compile_definitions(${EnvTarget}👉 operation.name 👈 PRIVATE 👉 context.config.shared_lib_export_definition 👈)
{% endfor %}

qt_add_library(${EnvTarget} "")

target_link_libraries(
    ${EnvTarget}
    PUBLIC
    Qt6::Core
    qtgql::qtgql
    ${EnvTarget}schema
    {% for operation in context.generation_output.operations -%}
    ${EnvTarget}👉 operation.name 👈
    {% endfor %}
)
