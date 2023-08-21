{% macro input_type_destructor(fields) -%}
    {% for f in fields -%}
    {% if f.type.is_input_object_type -%}
    {% if f.type.is_optional -%}
    if (👉 f.name 👈.has_value())
        delete 👉 f.name 👈.value();
    {% else %}
    delete 👉 f.name 👈;
    {% endif -%}
    {% endif -%}
    {% endfor -%}
{% endmacro %}