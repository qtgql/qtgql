{%- from "macros/initialize_proxy_field.jinja.hpp" import initialize_proxy_field -%}
{%- from "macros/deserialize_concrete_field.jinja.hpp" import  deserialize_concrete_field -%}
{%- from "macros/update_concrete_field.jinja.hpp" import  update_concrete_field -%}
{%- from "macros/update_proxy_field.jinja.cpp" import  update_proxy_field -%}
{%- from "macros/iterate_type_condition.jinja.hpp" import  iterate_type_condition -%}

#include "./👉 context.operation.name 👈.hpp"

namespace 👉 context.config.env_name 👈::👉context.ns👈{

// Interfaces
{% for interface in context.operation.interfaces -%}
std::shared_ptr<👉 interface.concrete.name 👈> 👉 interface.deserializer_name 👈(const QJsonObject& data, const 👉 context.operation.name 👈 * operation){
auto type_name = data.value("__typename").toString();
{% for choice in interface.choices -%}
{% set do_on_meets -%}
{% if interface.concrete.implements_node %}
auto cached_maybe = 👉 interface.concrete.name 👈::get_node(data.value("id").toString());
if(cached_maybe.has_value()){
auto node = cached_maybe.value();
👉 interface.updater_name 👈(node, data, operation);
return std::static_pointer_cast<👉 interface.concrete.name 👈>(node);
}
{% endif -%}
return std::static_pointer_cast<👉 interface.concrete.name 👈>(👉 choice.deserializer_name 👈(data, operation));
{% endset -%}
👉iterate_type_condition(choice,"type_name", do_on_meets, loop)👈
{% endfor -%}
throw qtgql::exceptions::InterfaceDeserializationError(type_name.toStdString());
}
{% endfor %}


{% for t in context.operation.narrowed_types -%}
// Constructor
{% set base_name -%}
👉 context.qtgql_types.ObjectTypeABC.last if not t.base_interface else t.base_interface.name 👈
{% endset -%}
{% if t.concrete.is_root -%}
👉 t.name 👈::👉 t.name 👈(👉 context.operation.name 👈 * operation): 👉 base_name 👈::👉 base_name 👈(operation){
    m_inst = 👉 t.concrete.name 👈::instance();
    auto m_inst_ptr = m_inst;
{% else -%}
    👉 t.name 👈::👉 t.name 👈(👉 context.operation.name 👈 * operation, const std::shared_ptr<👉 t.concrete.name 👈> &inst)
: m_inst{inst}, 👉 base_name 👈::👉 base_name 👈(operation)
{
    {% endif -%}
    m_operation = operation;
    {%- for field in t.fields -%}
    👉 initialize_proxy_field(field) 👈
    {% endfor -%}
    _qtgql_connect_signals();
}

void 👉 t.name 👈::_qtgql_connect_signals(){
{# connecting signals here, when the concrete changed it will be mirrored here. -#}
{% if t.concrete.is_root -%}
auto m_inst_ptr = m_inst;
{% else %}
auto m_inst_ptr = m_inst.get();
{% endif -%}
Q_ASSERT_X(m_inst_ptr, __FILE__, "Tried to instantiate a proxy object with an empty pointer!");
{% for field in t.fields -%}
connect(m_inst_ptr, &👉context.schema_ns👈::👉t.concrete.name👈::👉 field.concrete.signal_name 👈, this,
[&](){
👉update_proxy_field(field, context.operation)👈
});
{% endfor -%}
};

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
👉deserialize_concrete_field(f)👈
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
👉update_concrete_field(f,f.concrete, private_name=f.private_name, operation_pointer="operation")👈
{% endfor %}
};



// 👉 t.name 👈 Getters
{%for f in t.fields -%}
[[nodiscard]] const 👉 f.type.property_type 👈  👉 t.name 👈::👉 f.concrete.getter_name 👈() const {
{% if f.type.is_queried_object_type or f.type.is_model or f.type.is_queried_interface or f.type.is_queried_union %}
return 👉f.private_name👈;
{% else -%}
return m_inst->👉 f.concrete.getter_name 👈(👉f.build_variables_tuple_for_field_arguments.replace("operation", "m_operation")👈);
{%- endif -%}
};
{% endfor %}


{% if  not t.concrete.is_root -%}
void 👉 t.name 👈::qtgql_replace_concrete(const std::shared_ptr<👉 t.concrete.name 👈> & new_inst){
    if (new_inst == m_inst){
    return;
    }
    m_inst->disconnect(this);
    {% for field in t.fields -%}
    if(m_inst->👉 field.private_name 👈 != new_inst->👉 field.private_name 👈){
    👉update_proxy_field(field, context.operation)👈
    };
    {% endfor -%}
    m_inst = new_inst;
    _qtgql_connect_signals();
};
{% endif -%}
{% endfor %}
}
