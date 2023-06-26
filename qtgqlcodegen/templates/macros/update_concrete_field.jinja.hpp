{%- from "macros/deserialize_concrete_field.jinja.hpp" import  deserialize_concrete_field -%}
{% macro update_concrete_field(proxy_field,f_concrete, fset_name, private_name, operation_pointer="operation") -%}
{% set current -%}
{% if not proxy_field.is_root and proxy_field.variable_uses  -%}
inst->👉private_name👈.at(👉proxy_field.build_variables_tuple_for_field_arguments👈)
{% else -%}
inst->👉private_name👈
{% endif -%}
{%- endset -%}
{% set setter_end -%}
{% if not proxy_field.is_root and proxy_field.variable_uses  -%}
, 👉proxy_field.build_variables_tuple_for_field_arguments👈
{% endif -%}
{%- endset -%}

if (!data.value("👉f_concrete.name👈").isNull()){
{% if proxy_field.type.is_builtin_scalar -%}
{% if proxy_field.type.is_void -%}
/* deliberately empty */
{% else -%}
auto new_👉f_concrete.name👈 = data.value("👉f_concrete.name👈").👉 proxy_field.type.is_builtin_scalar.from_json_convertor 👈;
if (👉current👈 != new_👉f_concrete.name👈){
inst->👉fset_name👈(new_👉f_concrete.name👈 👉 setter_end 👈);
}
{% endif %}
{% elif proxy_field.type.is_custom_scalar %}
auto new_👉proxy_field.name👈 = 👉 proxy_field.type.is_custom_scalar.type_name() 👈();
new_👉proxy_field.name👈.deserialize(data.value("👉f_concrete.name👈"));
if (👉current👈 != new_👉proxy_field.name👈){
inst->👉fset_name👈(new_👉f_concrete.name👈 👉 setter_end 👈);
}
{% elif proxy_field.type.is_queried_object_type %}
{% if f_concrete.implements_node %}
auto 👉f_concrete.name👈_data = data.value("person").toObject();
if (👉current👈 && 👉current👈->get_id() == 👉f_concrete.name👈_data.value("id").toString()){
👉proxy_field.type.updater_name👈(👉current👈, 👉f_concrete.name👈_data,  👉operation_pointer👈);
}
else{
inst->👉fset_name👈(👉proxy_field.type.deserializer_name👈(data.value("👉f_concrete.name👈").toObject(), 👉operation_pointer👈) 👉 setter_end 👈);
}
{% endif %}
{% elif proxy_field.type.is_model %}
{% set setter %}inst->👉 proxy_field.concrete.setter_name 👈{% endset %}
👉deserialize_concrete_field(proxy_field, setter)👈
{% else %}
throw qtgql::exceptions::NotImplementedError({"👉proxy_field.type.__class__.__name__👈 is not supporting updates ATM"});
{% endif %}
}
{% if proxy_field.type.is_optional %}
else {
inst->👉fset_name👈({} 👉 setter_end 👈);
}
{% endif %}
{%- endmacro %}