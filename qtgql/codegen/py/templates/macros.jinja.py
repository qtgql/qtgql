{% macro deserialize_field(f, assign_to, include_selection_check=True) -%}
{% if include_selection_check %}
if '{{f.name}}' in config.selections.keys():
{% endif %}
    field_data = data.get('{{f.name}}', {{f.default_value}})
    {%if not (f.type.is_builtin_scalar or f.is_custom_scalar) %}
    {% if include_selection_check -%}
    inner_config = config.selections['{{f.name}}']
    {% else %}
    inner_config = config
    {% endif %}
    {% endif %}
    {% if f.type.is_object_type -%}
    if field_data:
        {{ assign_to }} = {{f.type.is_object_type.name}}.from_dict(
        parent,
        field_data,
        inner_config,
        metadata,
    )
    {% elif f.type.is_model -%}
    {% if f.type.is_model.is_object_type -%}
    {{ assign_to }} = QGraphQListModel(
        parent=parent,
        data=[{{f.type.is_model.is_object_type.name}}.from_dict(parent, data=node, config=inner_config, metadata=metadata) for
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
    {{ assign_to }} = QGraphQListModel(parent, data=model_data)
    {% endif %}
    {% elif f.type.is_builtin_scalar -%}
    {{ assign_to }} = field_data
    {% elif f.is_custom_scalar -%}
    {{ assign_to }} = SCALARS.{{f.is_custom_scalar.__name__}}.deserialize(field_data)
    {% elif f.type.is_enum -%}
    {{ assign_to }} = {{f.type.is_enum.name}}[field_data]
    {% elif f.type.is_union() -%}
    type_name = field_data['__typename']
    choice = inner_config.choices[type_name]
    {{ assign_to }} = __TYPE_MAP__[type_name].from_dict(parent, field_data, choice, metadata)
    {% endif %}
{%- endmacro %}



{% macro update_field(f, fset_name, private_name, include_selection_check=True) -%}
{% if include_selection_check %}
if '{{f.name}}' in config.selections.keys():
{% endif %}
    field_data = data.get('{{f.name}}', {{f.default_value}})
    {%if not (f.type.is_builtin_scalar or f.is_custom_scalar) %}
    {% if include_selection_check -%}
    inner_config = config.selections['{{f.name}}']
    {% else %}
    inner_config = config
    {% endif %}
    {% endif %}
    {% if f.type.is_object_type %}
    if not field_data:
        {{fset_name}}(None)
    else:
        {% if f.can_select_id %}
        if {{private_name}} and {{private_name}}._id == field_data.get('id', None):
            {{private_name}}.update(field_data, inner_config, metadata)
        else:
        {% endif %}
            {{fset_name}}({{f.type.is_object_type.name}}.from_dict(
                parent,
                field_data,
                inner_config,
                metadata
            ))
    {% elif f.type.is_model %}
    node_config = inner_config
    new_len = len(field_data)
    prev_len = {{private_name}}.rowCount()
    if new_len < prev_len:
        # crop the list to the arrived data length.
        {{private_name}}.removeRows(new_len, prev_len - new_len)
    for index, node in enumerate(field_data):
        id_ = node.get("id", None)
        if id_ and {{private_name}}._data[index].id == id_:
            # same node on that index just call update there is no need call model signals.
            {{private_name}}._data[index].update(field_data[index], node_config, metadata)
        else:
            # get or create node if wasn't on the correct index.
            # Note: it is safe to call [].insert(50, 50) (although index 50 doesn't exist).
            {% if f.type.is_model.is_object_type %}
            {{private_name}}.insert(index,
                                      {{f.type.is_model.is_object_type.name}}.from_dict(self, field_data[index], node_config, metadata))
            {% elif f.type.is_model.is_union %}
            type_name = node['__typename']
            choice = node_config.choices[type_name]
            {{private_name}}.insert(index,
                                      __TYPE_MAP__[type_name].from_dict(self, field_data[index],
                                                                        choice, metadata))
            {% endif %}
    {% elif f.type.is_builtin_scalar %}
    if {{private_name}} != field_data:
        {{fset_name}}(field_data)
    {% elif f.is_custom_scalar %}
    new = SCALARS.{{f.is_custom_scalar.__name__}}.deserialize(field_data)
    if new != {{private_name}}:
        {{fset_name}}(new)
    {% elif f.type.is_enum %}
    if {{private_name}}.name != field_data:
        {{fset_name}}({{f.type.is_enum.name}}[field_data])
    {% elif f.type.is_union() %}
    type_name = field_data['__typename']
    choice = inner_config.choices[type_name]
    if {{private_name}} and {{private_name}}._id == field_data['id']:
        {{private_name}}.update(field_data, choice, metadata)
    else:
        {{fset_name}}(__TYPE_MAP__[type_name].from_dict(parent, field_data, choice, metadata))
    {% endif %}
{%- endmacro %}


{% macro loose_field(f, private_name) -%}
        {% if f.type.is_object_type or f.type.is_union() %}
        if {{private_name}}:
            {{private_name}}.loose(metadata)
            {{private_name}} = None
        {% elif f.type.is_model.is_object_type or f.type.is_model.is_union %}
        if {{private_name}}:
            for node in {{private_name}}._data:
                node.loose(metadata)
            {{private_name}}.deleteLater()
            {{private_name}} = None
        {% endif %}
{%- endmacro %}
