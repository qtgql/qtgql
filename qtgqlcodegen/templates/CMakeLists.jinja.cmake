set(EnvTarget "👉 context.target_name 👈")
add_library(${EnvTarget} "")
add_library(generated::${EnvTarget} ALIAS ${EnvTarget})
# cmake-lint: disable=C0301


qt_add_qml_module(${EnvTarget}
        URI ${EnvTarget}
        SOURCES
        {% for file in context.sources -%}
        👉 file.path.as_posix() 👈
        {% endfor -%}
        RESOURCE_PREFIX :/qt/qml/
        )
target_link_libraries(${EnvTarget} PUBLIC Qt6::Core qtgql::qtgql)
target_include_directories(${EnvTarget} PUBLIC ${CMAKE_CURRENT_LIST_DIR})