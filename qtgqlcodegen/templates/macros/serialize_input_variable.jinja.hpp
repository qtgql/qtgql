{% macro serialize_input_variable(json_obj, variable, attr_name_overrid = "") -%}
{% set var_value_attr -%}
{% if variable.type.is_optional -%}
👉 attr_name_overrid or variable.name 👈.value()
{% else -%}
👉 attr_name_overrid or variable.name 👈
{% endif -%}
{% endset -%}
{% if variable.type.is_optional %}
if (👉 variable.name 👈.has_value()){
{% endif %}
{% if variable.type.is_input_list -%}
QJsonArray qtgql__👉 variable.name 👈_json;
for (const auto& node: 👉 var_value_attr 👈){
qtgql__👉 variable.name 👈_json.append(👉 variable.type.of_type.json_repr("node") 👈);
}
👉 json_obj 👈.insert("👉 variable.name 👈",  qtgql__👉 variable.name 👈_json);
{% else -%}
👉 json_obj 👈.insert("👉 variable.name 👈",  👉 variable.json_repr(var_value_attr) 👈);
{% endif -%}
{% if variable.type.is_optional %}
}
{% endif %}
{% endmacro %}