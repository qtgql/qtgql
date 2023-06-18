
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
[[nodiscard]] const 👉 f.type.fget_type 👈 & 👉 f.getter_name 👈({%- if f.arguments -%}👉 f.arguments_type 👈 & args {% endif %}) const{
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

{% macro deserialize_field(f, setter_name, operation_pointer = "operation",
                           do_after_deserialized = "") -%}

if (!data.value("👉f.name👈").isNull()){
{% if f.type.is_object_type -%}
👉 setter_name 👈(👉f.concrete.type.deserializer_name👈(data.value("👉f.name👈").toObject(), 👉operation_pointer👈));

{% elif f.type.is_interface -%}
if field_data:
        👉 setter_name 👈(👉f.type.is_interface.name👈.from_dict(
        parent,
        field_data,
        inner_config,
        👉operation_pointer👈,
    ))
{% elif f.type.is_model -%}
{% if f.type.is_model.is_object_type -%}
QList<👉f.type.is_model.member_type👈> obj_list;
for (const auto& node: data.value("👉f.name👈").toArray()){
    obj_list.append(👉 f.type.is_model.is_object_type.deserializer_name 👈(node.toObject(), 👉operation_pointer👈));
};
👉 setter_name 👈(👉operation_pointer👈.operation_id, obj_list);

{% elif f.type.is_model.is_interface -%}
👉 setter_name 👈(qtgql::ListModel(
    parent=parent,
    data=[👉f.type.is_model.is_interface.name👈.from_dict(parent, data=node, config=inner_config, metadata=👉operation_pointer👈) for
          node in field_data],))
{% elif f.type.is_model.is_union -%}
model_data = []
for node in field_data:
    type_name = node['__typename']
    choice = inner_👉config_name👈.choices[type_name]
    model_data.append(
        __TYPE_MAP__[type_name].from_dict(self, node,
                                          choice, 👉operation_pointer👈)
    )
👉 setter_name 👈(qtgql::ListModel(parent, data=model_data))
{% endif %}
{% elif f.type.is_builtin_scalar -%}
{% if f.type.is_void -%}
/* deliberately empty */
{% else -%}
👉 setter_name 👈(data.value("👉f.name👈").👉 f.type.is_builtin_scalar.from_json_convertor 👈);
{% endif %}
{% elif f.is_custom_scalar -%}
👉 f.name👈replace = 👉 f.is_custom_scalar.type_name 👈();
👉 f.name👈replace = 👉 f.is_custom_scalar.type_name 👈().deserialize(data.value("👉f.name👈"));
👉 setter_name 👈(👉 f.name👈replace);
{% elif f.type.is_enum -%}
👉 setter_name 👈(Enums::👉f.type.is_enum.map_name👈::by_name(data.value("👉f.name👈").toString());
{% elif f.type.is_union -%}
type_name = field_data['__typename']
choice = inner_👉config_name👈.choices[type_name]
👉 setter_name 👈(__TYPE_MAP__[type_name].from_dict(parent, field_data, choice, 👉operation_pointer👈));
{% endif -%} 👉 do_after_deserialized 👈
};
{%- endmacro %}


{% macro update_concrete_field(f,f_concrete, fset_name, private_name, operation_pointer="operation") -%}
if (!data.value("👉f_concrete.name👈").isNull()){
{% if f.type.is_builtin_scalar -%}
{% if f.type.is_void -%}
/* deliberately empty */
{% else -%}
auto new_👉f_concrete.name👈 = data.value("👉f_concrete.name👈").👉 f.type.is_builtin_scalar.from_json_convertor 👈;
if (inst->👉private_name👈 != new_👉f_concrete.name👈){
    inst->👉fset_name👈(new_👉f_concrete.name👈);
}
{% endif %}
{% elif f.type.is_custom_scalar %}
auto new_👉f_concrete.name👈 = 👉 f.is_custom_scalar.type_name 👈();
new_👉f_concrete.name👈.deserialize(data.value("👉f_concrete.name👈"));
if (inst->👉private_name👈 != new_👉f_concrete.name👈){
    inst->👉fset_name👈(new_👉f_concrete.name👈);
}
{% elif f.type.is_object_type %}
{% if f_concrete.type.implements_node %}
auto 👉f_concrete.name👈_data = data.value("person").toObject();
if (inst->👉private_name👈 && inst->👉private_name👈->get_id() == 👉f_concrete.name👈_data.value("id").toString()){
👉f_concrete.type.updater_name👈(inst->👉private_name👈, 👉f_concrete.name👈_data,  👉operation_pointer👈);
}
    else{
inst->👉fset_name👈(👉f.type.is_object_type.name👈::from_json(
        👉f_concrete.name👈_data,
👉operation_pointer👈
));
    }
{% endif %}
inst->👉fset_name👈(👉f.type.is_object_type.name👈::from_json(
        data.value("👉f_concrete.name👈").toObject(),
👉operation_pointer👈
));


{% else %}
throw qtgql::exceptions::NotImplementedError({"👉f.type.__class__.__name__👈 is not supporting updates ATM"});
{% endif %}
}
{% if f.type.is_optional %}
else {
inst->👉fset_name👈({});
}
{% endif %}
{%- endmacro %}


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