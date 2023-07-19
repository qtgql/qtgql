cmake_minimum_required(VERSION 3.20)
set(EnvTarget "👉 context.target_name 👈")
set(QTGQL_QML_PLUGIN_DIRECTORY qml/Generated/${EnvTarget})
cmake_minimum_required(VERSION 3.20)

project(${EnvTarget} LANGUAGES CXX)

# Configure general compilation
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(APPLE)
    set(CMAKE_OSX_ARCHITECTURES "arm64;x86_64" CACHE STRING "" FORCE)
endif()

find_package(Qt6 REQUIRED COMPONENTS Core Quick Qml)

if(QT_VERSION VERSION_GREATER_EQUAL "6.3")
    qt_standard_project_setup()
else()
    set(CMAKE_AUTOMOC ON)
    set(CMAKE_AUTORCC ON)
    set(CMAKE_AUTOUIC ON)
endif()
qt_policy(SET QTP0001 NEW)

add_library(${PROJECT_NAME}schema
        schema.hpp
        )
target_link_libraries(${PROJECT_NAME}schema
        PUBLIC
        Qt::Core
        qtgql::qtgql
        )
{% for operation in context.generation_output.operations -%}

qt_add_qml_module(${PROJECT_NAME}👉 operation.name 👈
        URI Generated.${PROJECT_NAME}.👉 operation.name 👈
        # Using PLUGIN_TARGET in static library compilation will cause link failure
        OUTPUT_DIRECTORY ${QTGQL_QML_PLUGIN_DIRECTORY}/👉 operation.name 👈
        # TYPEINFO "plugins.qmltypes"
        SOURCES
        {% for filespec in operation.sources -%}
        👉 filespec.path.as_posix() 👈
        {% endfor -%}
        )

target_link_libraries(${PROJECT_NAME}👉 operation.name 👈 PUBLIC
        Qt::CorePrivate
        Qt::QuickPrivate
        Qt::QmlPrivate
        ${PROJECT_NAME}schema
        qtgql::qtgql
        )
{% endfor %}

qt_add_library(${PROJECT_NAME} "")

target_link_libraries(
    ${PROJECT_NAME}
    PUBLIC
    ${PROJECT_NAME}schema
    {% for operation in context.generation_output.operations -%}
    ${PROJECT_NAME}👉 operation.name 👈
    {% endfor %}
)