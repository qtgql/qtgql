{% macro iterate_type_condition(choice, type_cond, do_on_meets, loop) -%}
{% if loop.first -%}
if (👉type_cond👈 == "👉choice.concrete.name👈"){
    👉 do_on_meets 👈
}
{% else -%}
else if (👉type_cond👈 == "👉choice.concrete.name👈"){
    👉 do_on_meets 👈
}
{% endif -%}
{% if loop.last -%}
else{
    throw qtgql::exceptions::InterfaceDeserializationError({👉type_cond👈.toStdString()});
}
{% endif -%}
{% endmacro -%}