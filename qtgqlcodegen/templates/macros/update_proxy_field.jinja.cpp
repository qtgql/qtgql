{%- from "macros/iterate_type_condition.jinja.hpp" import  iterate_type_condition -%}
{% macro update_proxy_field(field, operation) -%}
{% set new_concrete -%}
m_inst->👉field.concrete.getter_name👈(👉field.build_variables_tuple_for_field_arguments 👈)
{%- endset -%}

{% if field.type.is_model -%}
    {% if field.type.of_type.is_queried_object_type and field.type.of_type.concrete.implements_node -%}
    {#- // the nodes themselves are updated as per normal (via deserializers) and here we only need
        // to set the nodes at the correct index and append them if they weren't existed so far.
    -#}
    auto operation = qobject_cast<👉operation.name👈*>(this->parent());
    auto new_data = 👉new_concrete👈;
    auto new_len = new_data.size();
    auto prev_len = 👉field.private_name👈->rowCount();
    if (new_len < prev_len){
        👉field.private_name👈->removeRows(prev_len - 1, prev_len - new_len);
    }
    for (int i = 0; i < new_len; i++){
        auto concrete = new_data.at(i);
        if (i > prev_len - 1){
            👉field.private_name👈->insert(i, new 👉field.type.of_type.name👈(operation, concrete));
        }
        else if (👉field.private_name👈->get(i)->get_id() != concrete->m_id){
            delete 👉field.private_name👈->get(i);
            👉field.private_name👈->insert(i, new 👉field.type.of_type.name👈(operation, concrete));
        }
    }
    {% else %}
    throw qtgql::excepctions::NotImplementedError({"can't update this model type ATM"});
    {% endif %}
{% elif field.type.is_queried_object_type -%}
auto operation = qobject_cast<👉operation.name👈*>(this->parent());
auto concrete = 👉new_concrete👈;
delete 👉field.private_name👈;
👉field.private_name👈 = new 👉field.type.name👈(operation, concrete);
emit 👉 field.concrete.signal_name 👈();
{% elif field.type.is_queried_interface -%}
auto operation = qobject_cast<👉operation.name👈*>(this->parent());
auto concrete = 👉new_concrete👈;
delete 👉field.private_name👈;
auto 👉field.name👈_typename = concrete->__typename();
{%set type_cond -%}👉field.name👈_typename{% endset -%}
{% for choice in field.type.choices %}
{% set do_on_meets -%}
👉field.private_name👈 = qobject_cast<const 👉field.type.name👈 *>(new 👉choice.name👈(operation, std::static_pointer_cast<👉choice.concrete.name👈>(concrete)));
{% endset -%}
👉iterate_type_condition(choice,type_cond, do_on_meets, loop)👈
{% endfor %}
emit 👉 field.concrete.signal_name 👈();
{% else -%}
emit 👉 field.concrete.signal_name 👈();
{% endif -%}
{% endmacro %}