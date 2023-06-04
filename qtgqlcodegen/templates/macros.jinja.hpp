
{% macro concrete_type_fields(type) -%}
protected:
{% for f in type.fields -%}
👉 f.member_type 👈 👉 f.private_name 👈 = 👉 f.default_value 👈;
{% endfor %}
signals:
{%for f in type.fields -%}
void 👉 f.signal_name 👈();
{% endfor %}

public:
{%for f in type.fields %}
{% if f.is_custom_scalar %}
const 👉 f.is_custom_scalar.type_for_proxy 👈 & 👉 f.getter_name 👈() {
return 👉 f.private_name 👈.to_qt();
}
{% else %}
const 👉 f.member_type 👈 & 👉 f.getter_name 👈() const {
return 👉 f.private_name 👈;
}
{% endif %}
void 👉 f.setter_name 👈(const 👉 f.member_type 👈 &v)
{
👉 f.private_name 👈 = v;
emit 👉 f.signal_name 👈();
};
{% endfor %}
{% endmacro -%}


{% macro deserialize_field(f, assign_to, include_selection_check = True, config_name = "config", metadata_name = "metadata",
                           do_after_deserialized = "") -%}

if ({% if include_selection_check %}👉config_name👈.selections.contains("👉f.name👈") && {% endif %} !data.value("👉f.name👈").isNull()){
{% if f.type.is_object_type -%}

👉 assign_to 👈 = 👉f.type.is_object_type.name👈::from_json(data.value("👉f.name👈").toObject(),
{% if include_selection_check -%}
👉config_name👈.selections.value("👉f.name👈")
{% else -%}
👉config_name👈
{% endif -%}, 👉metadata_name👈);

{% elif f.type.is_interface -%}
if field_data:
        👉 assign_to 👈 = 👉f.type.is_interface.name👈.from_dict(
        parent,
        field_data,
        inner_config,
        👉metadata_name👈,
    )
{% elif f.type.is_model -%}
{% if f.type.is_model.is_object_type -%}
QList<👉f.type.is_model.member_type👈> obj_list;
for (const auto& node: data.value("👉f.name👈").toArray()){
    obj_list.append(👉 f.type.is_model.is_object_type.name 👈::from_json(node.toObject(), 👉config_name👈.selections.value("👉f.name👈"), 👉metadata_name👈));
};
👉 assign_to 👈.insert(👉metadata_name👈.operation_id, obj_list);

{% elif f.type.is_model.is_interface -%}
👉 assign_to 👈 = qtgql::ListModel(
    parent=parent,
    data=[👉f.type.is_model.is_interface.name👈.from_dict(parent, data=node, config=inner_config, metadata=👉metadata_name👈) for
          node in field_data],
)
{% elif f.type.is_model.is_union -%}
model_data = []
for node in field_data:
    type_name = node['__typename']
    choice = inner_👉config_name👈.choices[type_name]
    model_data.append(
        __TYPE_MAP__[type_name].from_dict(self, node,
                                          choice, 👉metadata_name👈)
    )
👉 assign_to 👈 = qtgql::ListModel(parent, data=model_data)
{% endif %}
{% elif f.type.is_builtin_scalar -%}
👉 assign_to 👈 = data.value("👉f.name👈").👉 f.type.is_builtin_scalar.from_json_convertor 👈;
{% elif f.is_custom_scalar -%}
👉 assign_to 👈 = 👉 f.is_custom_scalar.type_name 👈();
👉 assign_to 👈.deserialize(data.value("👉f.name👈"));
{% elif f.type.is_enum -%}
👉 assign_to 👈 = Enums::👉f.type.is_enum.map_name👈::by_name(data.value("👉f.name👈").toString());
{% elif f.type.is_union -%}
type_name = field_data['__typename']
choice = inner_👉config_name👈.choices[type_name]
👉 assign_to 👈 = __TYPE_MAP__[type_name].from_dict(parent, field_data, choice, 👉metadata_name👈);
{% endif -%} 👉 do_after_deserialized 👈
};
{%- endmacro %}


{% macro update_concrete_field(f, fset_name, private_name, config_name= "config", include_selection_check=True) -%}

if ({% if include_selection_check %}👉config_name👈.selections.contains("👉f.name👈") && {% endif %} !data.value("👉f.name👈").isNull()){
{% if f.type.is_builtin_scalar %}
auto new_👉f.name👈 = data.value("👉f.name👈").👉 f.type.is_builtin_scalar.from_json_convertor 👈;
if (👉private_name👈 != new_👉f.name👈){
    👉fset_name👈(new_👉f.name👈);
}
{% else %}
throw "not implemented";
{% endif %}
}
{%- endmacro %}


{% macro initialize_proxy_field(field) %}
{%set instance_of_concrete -%}
{% if field.is_root %}
concrete
{% else %}
m_inst->👉field.definition.getter_name 👈()
{% endif %}{% endset -%}

{% if field.type.is_object_type  and field.type.is_optional() %}
if (👉 instance_of_concrete 👈){
👉field.private_name👈 = new 👉field.type_name👈(this, 👉 instance_of_concrete 👈);
}
else{
👉field.private_name👈 = nullptr;
}
{% elif field.type.is_object_type %}
👉field.private_name👈 = new 👉field.type_name👈(this, 👉 instance_of_concrete 👈);
{% elif field.type.is_model.is_object_type %}
auto init_list_👉 field.name 👈 =  std::make_unique<QList<👉field.narrowed_type.name👈*>>();
for (const auto & node: 👉 instance_of_concrete 👈.value(OPERATION_ID)){
init_list_👉 field.name 👈->append(new 👉field.narrowed_type.name👈(this, node));
}
👉field.private_name👈 = new 👉 field.type_name 👈(this, std::move(init_list_👉 field.name 👈));
{% endif %}
{% endmacro %}