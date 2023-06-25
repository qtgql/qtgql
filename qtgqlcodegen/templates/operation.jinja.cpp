{%- from "macros/initialize_proxy_field.jinja.hpp" import initialize_proxy_field -%}
{%- from "macros/deserialize_concrete_field.jinja.hpp" import  deserialize_concrete_field -%}
{%- from "macros/update_concrete_field.jinja.hpp" import  update_concrete_field -%}
#include "./👉 context.operation.name 👈.hpp"

namespace 👉 context.config.env_name 👈::👉context.ns👈{

{% for interface in context.operation.interfaces -%}
std::shared_ptr<👉 interface.concrete.name 👈> 👉 interface.deserializer_name 👈(const QJsonObject& data, const 👉 context.operation.name 👈 * operation){
auto tp_name = data["__typename"].toString();
{% for impl in interface.implementations.values() -%}
if ("👉 impl.name 👈" == tp_name){
return std::static_pointer_cast<👉 interface.name 👈>(👉 impl.deserializer_name 👈(data, operation));
}
{% endfor %}
throw qtgql::exceptions::InterfaceDeserializationError(tp_name.toStdString());
}
{% endfor %}


{% for t in context.operation.narrowed_types %}
// Constructor
{% if t.concrete.is_root -%}
👉 t.name 👈::👉 t.name 👈(👉 context.operation.name 👈 * operation): QObject::QObject(operation){
    m_inst = 👉 t.concrete.name 👈::instance();
    auto m_inst_ptr = m_inst;
{% else -%}
👉 t.name 👈::👉 t.name 👈(👉 context.operation.name 👈 * operation, const std::shared_ptr<👉 t.concrete.name 👈> &inst)
: m_inst{inst}, QObject::QObject(operation)
{
    auto m_inst_ptr = m_inst.get();
    Q_ASSERT_X(m_inst_ptr, __FILE__, "Tried to instantiate a proxy object with an empty pointer!");
    {% endif -%}
    {%- for field in t.fields -%}
    👉 initialize_proxy_field(field) 👈
    {% endfor -%}
    {#- connecting signals here, when the concrete changed it will be mirrored here. -#}
    {%- for field in t.fields -%}
    connect(m_inst_ptr, &👉context.schema_ns👈::👉t.concrete.name👈::👉 field.concrete.signal_name 👈, this,
            [&](){emit 👉 field.concrete.signal_name 👈();});
    {% endfor -%}

}
// Deserialzier
{% if not t.concrete.is_root %}
std::shared_ptr<👉 t.concrete.name 👈> 👉 t.deserializer_name 👈(const QJsonObject& data, const 👉 context.operation.name 👈 * operation){
if (data.isEmpty()){
    return {};
}
{% if t.concrete.implements_node %}
auto cached_maybe = 👉 t.concrete.name 👈::get_node(data.value("id").toString());
if(cached_maybe.has_value()){
    auto node = cached_maybe.value();
    👉 t.updater_name 👈(node, data, operation);
    return node;
}
{% endif -%}
auto inst = 👉 t.concrete.name 👈::shared();
{% for f in t.fields -%}
{% set setter %}inst->👉 f.concrete.setter_name 👈{% endset %}
👉deserialize_concrete_field(f, setter)👈
{% endfor %}
{% if t.concrete. implements_node %}
👉 t.concrete.name 👈::ENV_CACHE()->add_node(inst);
{% endif %}
return inst;
};
{% endif %}

// Updater
void 👉 t.updater_name 👈(👉 t.concrete.member_type_arg 👈 inst, const QJsonObject &data, const 👉 context.operation.name 👈 * operation)
{
{%for f in t.fields -%}
👉update_concrete_field(f,f.concrete, fset_name=f.concrete.setter_name, private_name=f.private_name, operation_pointer="operation")👈
{% endfor %}
};
{% endfor %}
}

