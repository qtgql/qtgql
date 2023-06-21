{% macro initialize_proxy_field(field, operation_pointer = "operation") -%}
{%set instance_of_concrete -%}
m_inst->👉field.concrete.getter_name 👈(👉field.build_variables_tuple_for_field_arguments 👈)
{% endset -%}

{% if field.type.is_queried_object_type  and field.type.is_optional %}
if (👉 instance_of_concrete 👈){
👉field.private_name👈 = new 👉field.type_name👈(👉operation_pointer👈, 👉 instance_of_concrete 👈);
}
else{
👉field.private_name👈 = nullptr;
}
{% elif field.type.is_queried_object_type %}
👉field.private_name👈 = new 👉field.type_name👈(👉operation_pointer👈, 👉 instance_of_concrete 👈);
{% elif field.type.is_model and field.type.is_model.is_queried_object_type %}
auto init_list_👉 field.name 👈 =  std::make_unique<QList<👉field.narrowed_type.name👈*>>();
for (const auto & node: 👉 instance_of_concrete 👈.value(metadata.operation_id)){
init_list_👉 field.name 👈->append(new 👉field.narrowed_type.name👈(👉operation_pointer👈, node));
}
👉field.private_name👈 = new 👉 field.type_name 👈(this, std::move(init_list_👉 field.name 👈));
{% endif -%}
{% endmacro -%}