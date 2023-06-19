{% macro update_concrete_field(proxy_field,f_concrete, fset_name, private_name, operation_pointer="operation") -%}
if (!data.value("👉f_concrete.name👈").isNull()){
{% if proxy_field.type.is_builtin_scalar -%}
{% if proxy_field.type.is_void -%}
/* deliberately empty */
{% else -%}
auto new_👉f_concrete.name👈 = data.value("👉f_concrete.name👈").👉 proxy_field.type.is_builtin_scalar.from_json_convertor 👈;
if (inst->👉private_name👈 != new_👉f_concrete.name👈){
inst->👉fset_name👈(new_👉f_concrete.name👈);
}
{% endif %}
{% elif proxy_field.type.is_custom_scalar %}
auto new_👉proxy_field.name👈 = 👉 proxy_field.type.is_custom_scalar.type_name() 👈();
new_👉proxy_field.name👈.deserialize(data.value("👉proxy_field.name👈"));
if (inst->👉private_name👈 != new_👉proxy_field.name👈){
inst->👉fset_name👈(new_👉f_concrete.name👈);
}
{% elif proxy_field.type.is_object_type %}
{% if f_concrete.type.implements_node %}
auto 👉f_concrete.name👈_data = data.value("person").toObject();
if (inst->👉private_name👈 && inst->👉private_name👈->get_id() == 👉f_concrete.name👈_data.value("id").toString()){
👉f_concrete.type.updater_name👈(inst->👉private_name👈, 👉f_concrete.name👈_data,  👉operation_pointer👈);
}
else{
inst->👉fset_name👈(👉proxy_field.type.deserializer_name👈(
👉f_concrete.name👈_data,
👉operation_pointer👈
));
}
{% endif %}
inst->👉fset_name👈(👉proxy_field.type.deserializer_name👈(
        data.value("👉f_concrete.name👈").toObject(),
👉operation_pointer👈
));
{% else %}
throw qtgql::exceptions::NotImplementedError({"👉proxy_field.type.__class__.__name__👈 is not supporting updates ATM"});
{% endif %}
}
{% if proxy_field.type.is_optional %}
else {
inst->👉fset_name👈({});
}
{% endif %}
{%- endmacro %}