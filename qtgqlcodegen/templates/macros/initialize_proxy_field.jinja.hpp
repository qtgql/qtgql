{%- from "macros/iterate_type_condition.jinja.hpp" import  iterate_type_condition -%}
{% macro initialize_proxy_field(parent_type, field, operation_pointer = "operation") -%}

{% if field.cached_by_args -%}
auto args_for_👉field.name 👈 = 👉 parent_type.name 👈::👉field.variable_builder_name 👈( 👉 operation_pointer 👈);
{%set instance_of_concrete -%}
m_inst->👉field.concrete.getter_name 👈(args_for_👉field.name 👈)
{% endset -%}
{% else %}
{%set instance_of_concrete -%}
m_inst->👉field.concrete.getter_name 👈()
{% endset -%}
{% endif %}

{% if field.type.is_queried_object_type  and field.type.is_optional %}
if (👉 instance_of_concrete 👈){
👉field.private_name👈 = new 👉 field.type.type_name() 👈(👉operation_pointer👈, 👉 instance_of_concrete 👈);
}
{% elif field.type.is_queried_object_type %}
👉field.private_name👈 = new 👉field.type.type_name()👈(👉operation_pointer👈, 👉 instance_of_concrete 👈);
{% elif field.type.is_model and not field.type.of_type.is_builtin_scalar %}
    {% if  field.type.is_model.of_type.is_queried_object_type %}
    auto init_vec_👉 field.name 👈 =  std::vector<👉field.type.of_type.name👈*>();
    for (const auto & node: 👉 instance_of_concrete 👈){
    init_vec_👉 field.name 👈.push_back(new 👉field.type.of_type.name👈(👉operation_pointer👈, node));
    }
    👉field.private_name👈 = new qtgql::bases::ListModelABC<👉 field.type.of_type.property_type 👈>(this, std::move(init_vec_👉 field.name 👈));
    {% elif field.type.is_model.of_type.is_queried_union or field.type.is_model.of_type.is_queried_interface%}
    auto init_vec_👉 field.name 👈 =  std::vector<👉field.type.of_type.property_type👈>();
    for (const auto & node: 👉 instance_of_concrete 👈){
        auto 👉field.name👈_typename = node->__typename();
        {%set type_cond -%}👉field.name👈_typename{% endset -%}
        {% for choice in field.type.of_type.choices -%}
        {% set do_on_meets -%}
        init_vec_👉 field.name 👈.push_back(qobject_cast<👉 field.type.of_type.property_type 👈>(new 👉choice.type_name()👈(👉operation_pointer👈, std::static_pointer_cast<👉 choice.concrete.name 👈>(node))));
        {% endset -%}
        👉iterate_type_condition(choice,type_cond, do_on_meets, loop)👈
        {% endfor %}
    }
    👉field.private_name👈 = new qtgql::bases::ListModelABC<👉 field.type.of_type.property_type 👈>(this, std::move(init_vec_👉 field.name 👈));
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