set(SCHEMA_TARGET "👉 context.target_name 👈")
add_library(${SCHEMA_TARGET} "")
add_library(generated::${SCHEMA_TARGET} ALIAS ${SCHEMA_TARGET})
# cmake-lint: disable=C0301
target_sources(${SCHEMA_TARGET} PUBLIC 
{% for file in context.sources -%}
👉 file.path.as_posix() 👈
{% endfor -%}
)
target_link_libraries(${SCHEMA_TARGET} PUBLIC Qt6::Core qtgql::qtgql)
target_include_directories(${SCHEMA_TARGET} PUBLIC ${CMAKE_CURRENT_LIST_DIR})