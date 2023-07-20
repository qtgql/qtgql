{%- from "macros/iterate_type_condition.jinja.hpp" import  iterate_type_condition -%}
{% macro update_proxy_field(field, operation) -%}
{% set new_concrete -%}
m_inst->👉field.concrete.getter_name👈(👉field.build_variables_tuple_for_field_arguments 👈)
{%- endset -%}
auto operation = m_operation;
{% if field.type.is_model -%}
    auto new_data = 👉new_concrete👈;
    auto new_len = new_data.size();
    auto prev_len = 👉field.private_name👈->rowCount();
    if (new_len < prev_len){
        👉field.private_name👈->removeRows(prev_len - 1, prev_len - new_len);
    }
    for (int i = 0; i < new_len; i++){
        auto concrete = new_data.at(i);
    {% if field.type.of_type.is_queried_object_type -%}
        if (i > prev_len){
            👉field.private_name👈->insert(i, new 👉field.type.of_type.name👈(operation, concrete));
        } else {
            auto proxy_to_update = 👉field.private_name👈->get(i);
            if(proxy_to_update){
                proxy_to_update->qtgql_replace_concrete(concrete);
            }
            else{ {#// handle optionals no need to delete -#}
                👉field.private_name👈->insert(i, new 👉field.type.of_type.name👈(operation, concrete));
            }
        }

    {% elif field.type.of_type.is_queried_union or field.type.of_type.is_queried_interface %}
        auto 👉field.name👈_typename = concrete->__typename();
        {%set type_cond -%}👉field.name👈_typename{% endset -%}
        {% for choice in field.type.of_type.choices %}
        {% set do_on_meets -%}
        if (i > prev_len){
            👉field.private_name👈->insert(i, new 👉choice.name👈(operation, std::static_pointer_cast<👉choice.concrete.name👈>(concrete)));
        } else{
            auto proxy_to_update = 👉field.private_name👈->get(i);
            if (proxy_to_update && proxy_to_update->__typename() == "👉choice.concrete.name👈"){
                qobject_cast<👉choice.property_type👈>(proxy_to_update)->qtgql_replace_concrete(std::static_pointer_cast<👉choice.concrete.name👈>(concrete));
            }
            else{
                👉field.private_name👈->insert(i, new 👉choice.name👈(operation, std::static_pointer_cast<👉choice.concrete.name👈>(concrete)));
                delete proxy_to_update; {# // might have been optional or the type_name changed #}
            }

        }

        {% endset %}
        👉iterate_type_condition(choice,type_cond, do_on_meets, loop)👈
        {% endfor %}
    {% else %}
    throw qtgql::exceptions::NotImplementedError({""
                                                  "can't update model of 👉field.type.of_type.__class__👈"});
    {% endif %}
    }
{% elif field.type.is_queried_object_type -%}
auto concrete = 👉new_concrete👈;
if (👉field.private_name👈){
    👉field.private_name👈->qtgql_replace_concrete(concrete);
}
else{
    👉field.private_name👈 = new 👉field.type.name👈(operation, concrete);
    emit 👉 field.concrete.signal_name 👈();
}
{% elif field.type.is_queried_interface or field.type.is_queried_union -%}
auto concrete = 👉new_concrete👈;
auto 👉field.name👈_typename = concrete->__typename();
{%set type_cond -%}👉field.name👈_typename{% endset -%}
{% for choice in field.type.choices %}
{% set do_on_meets -%}
if (👉field.private_name👈 && 👉field.private_name👈->__typename() == "👉choice.concrete.name👈"){
qobject_cast<👉choice.property_type👈>(👉field.private_name👈)->qtgql_replace_concrete(std::static_pointer_cast<👉choice.concrete.name👈>(concrete));
}
else{
    delete 👉field.private_name👈; {# // might have been optional or the type_name changed #}
    👉field.private_name👈 = qobject_cast<👉field.type.property_type👈>(new 👉choice.name👈(operation, std::static_pointer_cast<👉choice.concrete.name👈>(concrete)));
}
{% endset -%}
👉iterate_type_condition(choice,type_cond, do_on_meets, loop)👈
{% endfor %}
emit 👉 field.concrete.signal_name 👈();
{% else -%}
emit 👉 field.concrete.signal_name 👈();
{% endif -%}
{% endmacro %}