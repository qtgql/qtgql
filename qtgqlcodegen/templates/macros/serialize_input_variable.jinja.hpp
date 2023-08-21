{% macro serialize_input_variable(json_obj, variable, attr_name , json_name) -%}
{% set p_var_value_attr -%}
{% if variable.type.is_optional -%}
👉 attr_name 👈.value()
{% else -%}
👉 attr_name 👈
{% endif -%}
{% endset -%}
{% if variable.type.is_optional %}
if (👉 attr_name 👈.has_value()){
{% endif %}
{% if variable.type.is_input_list -%}
QJsonArray qtgql__👉 variable.name 👈_json;
for (const auto& node: 👉 p_var_value_attr 👈){
qtgql__👉 variable.name 👈_json.append(👉 variable.type.of_type.json_repr("node", accessor=".") 👈);
}
👉 json_obj 👈.insert("👉 json_name 👈",  qtgql__👉 variable.name 👈_json);
{% else -%}
👉 json_obj 👈.insert("👉 json_name 👈",  👉 variable.json_repr(p_var_value_attr) 👈);
{% endif -%}
{% if variable.type.is_optional %}
}
{% endif %}
{% endmacro %}