{% macro proxy_type_fields(t, context) -%}

{% for f in t.fields -%}
Q_PROPERTY(const 👉 f.property_type 👈 👉 f.name 👈 READ 👉 f.concrete.getter_name 👈 NOTIFY 👉 f.concrete.signal_name 👈);
{% endfor %}
signals:
{%for f in t.fields -%}
void 👉 f.concrete.signal_name 👈();
{% endfor %}

{# members #}
{% if context.debug -%}
public: // WARNING: members are public because you have debug=True in your config file.
{% else %}
protected:
{% endif %}
{% if t.concrete.is_root %} {# // root types are singletons, no need for shared ptr -#}
👉context.schema_ns👈::👉 t.concrete.name 👈 * m_inst;
{% else %}
const std::shared_ptr<👉context.schema_ns👈::👉 t.concrete.name 👈> m_inst;
{% endif %}
{% for ref_field in t.references -%}
const 👉ref_field.property_type👈 m_👉ref_field.name👈 = {};
{% endfor %}
{%- for model_field in t.models -%}
👉 model_field.property_type 👈 👉model_field.private_name👈;
{% endfor %}

public:
{% for f in t.fields -%}
{%- if f.type.is_queried_object_type or f.type.is_model or f.type.is_queried_interface %}
[[nodiscard]] inline const 👉 f.property_type 👈  👉 f.concrete.getter_name 👈() const {
return m_👉f.name👈;
{%- else -%}
[[nodiscard]] inline const 👉 f.property_type 👈 👉 f.concrete.getter_name 👈() const {
{% if f.type.is_queried_object_type -%}
return *m_👉f.name👈; // TODO: I think this is redundant.
{% else -%}
return m_inst->👉 f.concrete.getter_name 👈();
{% endif -%}
{%- endif -%}
};
{% endfor -%}
{% endmacro %}