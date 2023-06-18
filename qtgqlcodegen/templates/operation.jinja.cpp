{% import "macros.jinja.hpp" as macros -%}
#include "./👉 context.operation.name 👈.hpp"

namespace 👉 context.config.env_name 👈::👉context.ns👈{

{% for interface in context.interfaces -%}
std::shared_ptr<👉 interface.name 👈> 👉 interface.deserializer_name 👈(const QJsonObject& data, const 👉 context.operation.name 👈 * operation){
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
👉 t.name 👈::👉 t.name 👈(👉 context.operation.name 👈 * operation, const std::shared_ptr<👉 t.concrete.name 👈> &inst)
: m_inst{inst}, QObject::QObject(operation)
{
    {%- for field in t.fields -%}
    👉 macros.initialize_proxy_field(field) 👈
    {#- updates logic -#}
    connect(m_inst.get(), &👉context.schema_ns👈::👉t.concrete.name👈::👉 field.concrete.signal_name 👈, this,
            [&](){emit 👉 field.concrete.signal_name 👈();});
    {% endfor -%}
}
std::shared_ptr<👉 t.concrete.name 👈> 👉 t.concrete.deserializer_name 👈(const QJsonObject& data, const 👉 context.operation.name 👈 * operation){
if (data.isEmpty()){
    return {};
}
{% if t.concrete.implements_node %}
auto cached_maybe = 👉 t.concrete.name 👈::get_node(data.value("id").toString());
if(cached_maybe.has_value()){
    auto node = cached_maybe.value();
    👉 t.concrete.updater_name 👈(node, data, operation);
    return node;
}
{% endif %}

auto inst = std::make_shared<👉 t.concrete.name 👈>();
{% for f in t.fields -%}
{% set setter %}inst->👉 f.concrete.setter_name 👈{% endset %}
👉macros.deserialize_field(f, setter)👈
{% endfor %}
{% if t.concrete. implements_node %}
👉 t.concrete.name 👈::ENV_CACHE()->add_node(inst);
{% endif %}
return inst;
};

void 👉 t.concrete.updater_name 👈(👉 t.concrete.member_type 👈 &inst, const QJsonObject &data, const 👉 context.operation.name 👈 * operation)
{
{%for f in t.fields -%}
👉 macros.update_concrete_field(f,f.concrete, fset_name=f.concrete.setter_name, private_name=f.private_name, operation_pointer="operation") 👈
{% endfor %}
};
{% endfor %}
}

