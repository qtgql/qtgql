{%- from "macros/deserialize_concrete_field.jinja.hpp" import  deserialize_concrete_field -%}
{%- from "macros/iterate_type_condition.jinja.hpp" import  iterate_type_condition -%}
{% macro update_concrete_field(proxy_field,f_concrete, private_name, operation_pointer="operation") -%}
{% if proxy_field.variable_uses  -%}
👉f_concrete.arguments_type👈 👉private_name👈_args = 👉proxy_field.build_variables_tuple_for_field_arguments👈;
{% endif %}
{%- set current -%}
{% if proxy_field.variable_uses  -%}
inst->👉private_name👈.at(👉private_name👈_args)
{%- else -%}
inst->👉private_name👈
{%- endif -%}
{%- endset -%}
{% set setter_end -%}
{% if proxy_field.variable_uses -%}
, 👉private_name👈_args
{% endif -%}
{%- endset -%}
{%- set setter_name -%}inst->👉 proxy_field.concrete.setter_name 👈{% endset -%}

{%- if proxy_field.is_root and f_concrete.type.is_object_type or f_concrete.type.is_interface or f_concrete.type.is_union -%}
{#- // root fields that has no default value might not have value even if they are not optional -#}
{% if proxy_field.variable_uses  -%}
if (!inst->👉private_name👈.contains(👉private_name👈_args))
{% else -%}
if (!👉current👈)
{% endif %}
{
    {#- // Note: we can't use deserializer name since it might not be an object type. -#}
    👉deserialize_concrete_field(proxy_field)👈
}
else
{% endif -%}
if (!data.value("👉f_concrete.name👈").isNull()){
{% if proxy_field.type.is_builtin_scalar -%}
{% if proxy_field.type.is_void -%}
/* deliberately empty */
{% else -%}
auto new_👉f_concrete.name👈 = data.value("👉f_concrete.name👈").👉 proxy_field.type.is_builtin_scalar.from_json_convertor 👈;
if (👉current👈 != new_👉f_concrete.name👈){
👉 setter_name 👈(new_👉f_concrete.name👈 👉 setter_end 👈);
}
{% endif %}
{% elif proxy_field.type.is_custom_scalar %}
auto new_👉proxy_field.name👈 = 👉 proxy_field.type.is_custom_scalar.type_name() 👈();
new_👉proxy_field.name👈.deserialize(data.value("👉f_concrete.name👈"));
if (👉current👈 != new_👉proxy_field.name👈){
👉 setter_name 👈(new_👉f_concrete.name👈 👉 setter_end 👈);
}
{% elif proxy_field.type.is_queried_object_type %}
    auto 👉f_concrete.name👈_data = data.value("👉f_concrete.name👈").toObject();
    {% if f_concrete.implements_node %}
    if (👉current👈 && 👉current👈->get_id() == 👉f_concrete.name👈_data.value("id").toString()){
    👉proxy_field.type.updater_name👈(👉current👈, 👉f_concrete.name👈_data,  👉operation_pointer👈);
    }
    else{
    👉 setter_name 👈(👉proxy_field.type.deserializer_name👈(👉f_concrete.name👈_data, 👉operation_pointer👈) 👉 setter_end 👈);
    }
    {% else %}
    👉proxy_field.type.updater_name👈(👉current👈, 👉f_concrete.name👈_data,  👉operation_pointer👈);
    {% endif %}
{% elif proxy_field.type.is_model %}
👉deserialize_concrete_field(proxy_field)👈
{% elif proxy_field.type.is_enum %}
auto new_👉f_concrete.name👈= Enums::👉proxy_field.type.is_enum.map_name👈::by_name(data.value("👉proxy_field.name👈").toString());
if (👉current👈 != new_👉f_concrete.name👈){
👉 setter_name 👈(new_👉f_concrete.name👈 👉 setter_end 👈);
}
{% elif proxy_field.type.is_queried_interface or proxy_field.type.is_queried_union %}
auto 👉f_concrete.name👈_data = data.value("👉f_concrete.name👈").toObject();
auto 👉f_concrete.name👈_typename  = 👉f_concrete.name👈_data.value("__typename").toString();
{%set type_cond -%}👉f_concrete.name👈_typename{% endset -%}
{% for choice in proxy_field.type.choices %}
{% set do_on_meets -%}
{% if choice.implements_node %}
auto 👉f_concrete.name👈_casted = std::static_pointer_cast<👉choice.concrete.name👈>(👉current👈);
if (👉current👈 && 👉f_concrete.name👈_casted->get_id() == 👉f_concrete.name👈_data.value("id").toString()){
👉choice.updater_name👈(👉f_concrete.name👈_casted, 👉f_concrete.name👈_data,  👉operation_pointer👈);
}
else{
👉 setter_name 👈(👉choice.deserializer_name👈(👉proxy_field.name👈_data, 👉operation_pointer👈) 👉 setter_end 👈);
}
{% else %}
👉choice.updater_name👈(std::static_pointer_cast<👉choice.concrete.name👈>(👉current👈), 👉f_concrete.name👈_data,  👉operation_pointer👈);
{% endif %}
{% endset -%}
👉iterate_type_condition(choice,type_cond, do_on_meets, loop)👈
{% endfor %}
{% else %}
throw qtgql::exceptions::NotImplementedError({"👉proxy_field.type.__class__.__name__👈 is not supporting updates ATM"});
{% endif %}
}
{% if proxy_field.type.is_optional %}
else {
👉 setter_name 👈({} 👉 setter_end 👈);
}
{% endif %}
{%- endmacro %}