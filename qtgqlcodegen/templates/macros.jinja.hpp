
{% macro concrete_type_fields(type) -%}
public:
{% for f in type.unique_fields -%}
👉 f.type_with_args 👈 👉 f.private_name 👈 = 👉 f.type.default_value 👈;
{% endfor %}
signals:
{%for f in type.unique_fields -%}
void 👉 f.signal_name 👈();
{% endfor %}

public:
{%for f in type.unique_fields %}
[[nodiscard]] const 👉 f.type.fget_type 👈 &👉 f.getter_name 👈(
        {%- if f.arguments -%}👉 f.arguments_type 👈 & args {% endif -%}
        ) {%- if f.type.getter_is_constable -%}const{% endif %}{
{%- if f.arguments -%}
{% set f_private_name %}👉 f.private_name 👈.at(args){% endset %}
{% else -%}
{% set f_private_name %}👉 f.private_name 👈{% endset %}
{% endif -%}
{% if f.is_custom_scalar -%}
return 👉 f_private_name 👈.to_qt();
{% else -%}
return 👉 f_private_name 👈;
{% endif -%}
}
void 👉 f.setter_name 👈(const 👉 f.type.member_type 👈 &v {% if f.arguments %}, 👉 f.arguments_type 👈 & args {% endif %})
{
{%- if f.arguments -%}
{% set f_private_name %}👉 f.private_name 👈.at(args){% endset %}
{% else -%}
{% set f_private_name %}👉 f.private_name 👈{% endset %}
{% endif -%}
👉 f_private_name 👈 = v;
emit 👉 f.signal_name 👈();
};
{% endfor %}
{% endmacro -%}

{% macro initialize_proxy_field(field, operation_pointer = "operation") -%}
{%set instance_of_concrete -%}
{% if field.is_root -%}
concrete
{% else -%}
m_inst->👉field.concrete.getter_name 👈()
{% endif -%}{% endset -%}

{% if field.type.is_object_type  and field.type.is_optional %}
if (👉 instance_of_concrete 👈){
👉field.private_name👈 = new 👉field.type_name👈(👉operation_pointer👈, 👉 instance_of_concrete 👈);
}
else{
👉field.private_name👈 = nullptr;
}
{% elif field.type.is_object_type %}
👉field.private_name👈 = new 👉field.type_name👈(👉operation_pointer👈, 👉 instance_of_concrete 👈);
{% elif field.type.is_model and field.type.is_model.is_object_type %}
auto init_list_👉 field.name 👈 =  std::make_unique<QList<👉field.narrowed_type.name👈*>>();
for (const auto & node: 👉 instance_of_concrete 👈.value(metadata.operation_id)){
init_list_👉 field.name 👈->append(new 👉field.narrowed_type.name👈(👉operation_pointer👈, node));
}
👉field.private_name👈 = new 👉 field.type_name 👈(this, std::move(init_list_👉 field.name 👈));
{% endif %}
{% endmacro %}