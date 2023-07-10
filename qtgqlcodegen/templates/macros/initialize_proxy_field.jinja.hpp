{%- from "macros/iterate_type_condition.jinja.hpp" import  iterate_type_condition -%}
{% macro initialize_proxy_field(field, operation_pointer = "operation") -%}
{%set instance_of_concrete -%}
m_inst->👉field.concrete.getter_name 👈(👉field.build_variables_tuple_for_field_arguments 👈)
{% endset -%}

{% if field.type.is_queried_object_type  and field.type.is_optional %}
if (👉 instance_of_concrete 👈){
👉field.private_name👈 = new 👉field.type_name👈(👉operation_pointer👈, 👉 instance_of_concrete 👈);
}
{% elif field.type.is_queried_object_type %}
👉field.private_name👈 = new 👉field.type_name👈(👉operation_pointer👈, 👉 instance_of_concrete 👈);
{% elif field.type.is_model  %}
    {% if  field.type.is_model.of_type.is_queried_object_type %}
    auto init_list_👉 field.name 👈 =  std::make_unique<QList<👉field.type.of_type.name👈*>>();
    for (const auto & node: 👉 instance_of_concrete 👈){
    init_list_👉 field.name 👈->append(new 👉field.type.of_type.name👈(👉operation_pointer👈, node));
    }
    👉field.private_name👈 = new qtgql::bases::ListModelABC<👉 field.type.of_type.name 👈>(this, std::move(init_list_👉 field.name 👈));
    {% elif field.type.is_model.of_type.is_queried_union or field.type.is_model.of_type.is_queried_interface %}
    auto init_list_👉 field.name 👈 =  std::make_unique<QList<👉field.type.of_type.property_type👈>>();
    for (const auto & node: 👉 instance_of_concrete 👈){
        auto 👉field.name👈_typename = node->__typename();
        {%set type_cond -%}👉field.name👈_typename{% endset -%}
        {% for choice in field.type.of_type.choices -%}
        {% set do_on_meets -%}
        init_list_👉 field.name 👈->append(qobject_cast<👉 field.type.of_type.property_type 👈>(new 👉choice.type_name()👈(👉operation_pointer👈, std::static_pointer_cast<👉 choice.concrete.name 👈>(node))));
        {% endset -%}
        👉iterate_type_condition(choice,type_cond, do_on_meets, loop)👈
        {% endfor %}
    }
    👉field.private_name👈 = new qtgql::bases::ListModelABC<👉 field.type.of_type.type_name() 👈>(this, std::move(init_list_👉 field.name 👈));
    {% else %}
    not implemented
    {% endif %}
{% elif field.type.is_queried_interface or  field.type.is_queried_union %}
auto concrete_👉field.name👈 = 👉 instance_of_concrete 👈;
auto 👉field.name👈_typename = concrete_👉field.name👈->__typename();
{%set type_cond -%}👉field.name👈_typename{% endset -%}
{% for choice in field.type.choices -%}
{% set do_on_meets -%}
👉field.private_name👈 = qobject_cast<👉 field.type.property_type 👈>(new 👉choice.type_name()👈(👉operation_pointer👈, std::static_pointer_cast<👉 choice.concrete.name 👈>(concrete_👉field.name👈)));
{% endset -%}
👉iterate_type_condition(choice,type_cond, do_on_meets, loop)👈
{% endfor %}
{% endif -%}
{% endmacro -%}