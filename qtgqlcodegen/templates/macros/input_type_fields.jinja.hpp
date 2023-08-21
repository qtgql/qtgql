{% macro input_type_fields (fields) -%}
{%- for f in fields -%}
{% if f.type.is_optional -%}
std::optional<👉 f.type.type_name() 👈> 👉 f.name 👈 = {};
{% else -%}
👉 f.type.type_name() 👈 👉 f.name 👈;
{% endif -%}
{%- endfor -%}
{% endmacro %}
// TODO: delete this