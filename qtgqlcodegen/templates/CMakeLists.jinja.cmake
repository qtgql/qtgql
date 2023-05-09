set(SCHEMA_TARGET "👉 context.target_name 👈")
add_library(${SCHEMA_TARGET} "")
add_library(__generated__::${SCHEMA_TARGET} ALIAS ${SCHEMA_TARGET})
target_sources(${SCHEMA_TARGET} PUBLIC 
{% for file in context.sources -%}
👉 file.path 👈
{% endfor -%}
)
target_link_libraries(${SCHEMA_TARGET} PUBLIC Qt6::Core qtgql::wstransport qtgql::bases)
target_include_directories(${SCHEMA_TARGET} PUBLIC ${CMAKE_CURRENT_LIST_DIR})