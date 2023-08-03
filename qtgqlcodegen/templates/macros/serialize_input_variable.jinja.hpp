{% macro serialize_input_variable(json_obj, variable) -%}
if (👉 variable.name 👈.has_value()){
{% if variable.type.is_input_list -%}
QJsonArray 👉 variable.name 👈_json;
for (const auto& node: 👉 variable.name 👈.value()){
👉 variable.name 👈_json.append(👉 variable.type.of_type.json_repr("node") 👈);
}
__ret.insert("👉 variable.name 👈",  👉 variable.name 👈_json);
{% else -%}
__ret.insert("👉 variable.name 👈",  👉 variable.json_repr() 👈);
{% endif -%}
}
{% endmacro %}