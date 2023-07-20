{% macro proxy_type_fields(t, context) -%}
Q_OBJECT
QML_ELEMENT
QML_UNCREATABLE("QtGql does not supports instantiation via qml")
Q_PROPERTY(QString  __typeName READ __typename CONSTANT)

{% for f in t.fields -%}
Q_PROPERTY(const 👉 f.type.property_type 👈 👉 f.name 👈 READ 👉 f.concrete.getter_name 👈 NOTIFY 👉 f.concrete.signal_name 👈);
{% endfor %}
signals:
{%for f in t.fields -%}
void 👉 f.concrete.signal_name 👈();
{% endfor %}
{# members -#}
{% if context.debug -%}
public: // WARNING: members are public because you have debug=True in your config file.
{% else -%}
protected:
{% endif -%}
{% if t.concrete.is_root -%} {# // root types are singletons, no need for shared ptr -#}
👉context.schema_ns👈::👉 t.concrete.name 👈 * m_inst;
{% else -%}
std::shared_ptr<👉context.schema_ns👈::👉 t.concrete.name 👈> m_inst;
{% endif -%}
{% for ref_field in t.references -%}
👉ref_field.type.property_type👈 👉ref_field.private_name👈 = {};
{% endfor %}
{%- for model_field in t.models -%}
👉 model_field.type.property_type 👈 👉model_field.private_name👈;
{% endfor %}
{% endmacro %}