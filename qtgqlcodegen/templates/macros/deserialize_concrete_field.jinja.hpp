{% macro deserialize_concrete_field(proxy_field, setter_name, operation_pointer = "operation",
                           do_after_deserialized = "") -%}
{% set setter_end -%}
{% if proxy_field.cached_by_args %}
, 👉proxy_field.build_variables_tuple_for_field_arguments👈
{% endif -%}
{% endset -%}
if (!data.value("👉proxy_field.name👈").isNull()){
{% if proxy_field.type.is_queried_object_type -%}
👉 setter_name 👈(👉proxy_field.type.deserializer_name👈(data.value("👉proxy_field.name👈").toObject(), 👉operation_pointer👈) 👉 setter_end 👈);

{% elif proxy_field.type.is_queried_interface -%}
if field_data:
👉 setter_name 👈(👉proxy_field.type.is_interface.name👈.from_dict(
        parent,
        field_data,
        inner_config,
👉operation_pointer👈,
👉 setter_end 👈);
{% elif proxy_field.type.is_model -%}
{% if proxy_field.type.is_model.of_type.is_queried_object_type -%}
👉proxy_field.concrete.type.member_type👈 obj_list;
for (const auto& node: data.value("👉proxy_field.name👈").toArray()){
obj_list.append(👉 proxy_field.type.is_model.of_type.is_queried_object_type.deserializer_name 👈(node.toObject(), 👉operation_pointer👈));
};
👉 setter_name 👈(obj_list👉 setter_end 👈);

{% elif proxy_field.type.is_model.is_interface -%}
👉 setter_name 👈(qtgql::ListModel(
        parent=parent,
        data=[👉proxy_field.type.is_model.is_interface.name👈.from_dict(parent, data=node, config=inner_config, metadata=👉operation_pointer👈) for
node in field_data],)👉 setter_end 👈);
{% elif proxy_field.type.is_model.is_union -%}
model_data = []
for node in field_data:
type_name = node['__typename']
choice = inner_👉config_name👈.choices[type_name]
model_data.append(
        __TYPE_MAP__[type_name].from_dict(self, node,
        choice, 👉operation_pointer👈)
)
👉 setter_name 👈(qtgql::ListModel(parent, data=model_data)👉 setter_end 👈);
{% endif %}
{% elif proxy_field.type.is_builtin_scalar -%}
{% if proxy_field.type.is_void -%}
/* deliberately empty */
{% else -%}
👉 setter_name 👈(data.value("👉proxy_field.name👈").👉 proxy_field.type.is_builtin_scalar.from_json_convertor 👈 👉 setter_end 👈);
{% endif %}
{% elif proxy_field.type.is_custom_scalar -%}
auto new_👉proxy_field.name👈 = 👉 proxy_field.type.is_custom_scalar.type_name() 👈();
new_👉proxy_field.name👈.deserialize(data.value("👉proxy_field.name👈"));
👉 setter_name 👈(new_👉proxy_field.name👈 👉 setter_end 👈);
{% elif proxy_field.type.is_enum -%}
👉 setter_name 👈(Enums::👉proxy_field.type.is_enum.map_name👈::by_name(data.value("👉proxy_field.name👈").toString())👉 setter_end 👈);
{% elif proxy_field.type.is_union -%}
type_name = field_data['__typename']
choice = inner_👉config_name👈.choices[type_name]
👉 setter_name 👈(__TYPE_MAP__[type_name].from_dict(parent, field_data, choice, 👉operation_pointer👈)👉 setter_end 👈);;
{% endif -%} 👉 do_after_deserialized 👈
};
{%- endmacro %}
