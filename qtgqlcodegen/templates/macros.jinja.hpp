{% macro deserialize_field(f, assign_to, include_selection_check = True) -%}

if ({% if include_selection_check %}config.selections.contains("👉f.name👈") && {% endif %} !data.value("👉f.name👈").isNull()){
{% if f.type.is_object_type -%}

  👉 assign_to 👈 = 👉f.type.is_object_type.name👈.from_dict(
  parent,
  field_data,
  inner_config,
  metadata,

);

{% elif f.type.is_interface -%}
if field_data:
        👉 assign_to 👈 = 👉f.type.is_interface.name👈.from_dict(
        parent,
        field_data,
        inner_config,
        metadata,
    )
{% elif f.type.is_model -%}
{% if f.type.is_model.is_object_type -%}
👉 assign_to 👈 = qtgql::ListModel(
  parent=parent,
  data=[👉f.type.is_model.is_object_type.name👈.from_dict(parent, data=node, config=inner_config, metadata=metadata) for
        node in field_data],
)
{% elif f.type.is_model.is_interface -%}
👉 assign_to 👈 = qtgql::ListModel(
    parent=parent,
    data=[👉f.type.is_model.is_interface.name👈.from_dict(parent, data=node, config=inner_config, metadata=metadata) for
          node in field_data],
)
{% elif f.type.is_model.is_union -%}
model_data = []
for node in field_data:
    type_name = node['__typename']
    choice = inner_config.choices[type_name]
    model_data.append(
        __TYPE_MAP__[type_name].from_dict(self, node,
                                          choice, metadata)
    )
👉 assign_to 👈 = qtgql::ListModel(parent, data=model_data)
{% endif %}
{% elif f.type.is_builtin_scalar -%}
👉 assign_to 👈 = data.value("👉f.name👈").👉 f.type.is_builtin_scalar.from_json_convertor 👈;
{% elif f.is_custom_scalar -%}
👉 assign_to 👈 = 👉 f.is_custom_scalar.type_name 👈();
👉 assign_to 👈.deserialize(data.value("👉f.name👈"));
{% elif f.type.is_enum -%}
👉 assign_to 👈 = 👉f.type.is_enum.name👈[field_data];
{% elif f.type.is_union -%}
type_name = field_data['__typename']
choice = inner_config.choices[type_name]
👉 assign_to 👈 = __TYPE_MAP__[type_name].from_dict(parent, field_data, choice, metadata);
{% endif -%}
};
{%- endmacro %}



{% macro props(type) -%}
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
const 👉 f.is_custom_scalar.property_type 👈 & 👉 f.getter_name 👈() {
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
