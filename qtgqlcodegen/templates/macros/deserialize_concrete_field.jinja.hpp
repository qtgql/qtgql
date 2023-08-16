{%- from "macros/iterate_type_condition.jinja.hpp" import  iterate_type_condition -%}
{% macro deserialize_concrete_field(parent_proxy_type, proxy_field, operation_pointer = "operation",
                           do_after_deserialized = "") -%}
{% set setter_name %}inst->👉 proxy_field.concrete.setter_name 👈{% endset %}
{% set setter_end -%}
{% if proxy_field.cached_by_args %}
, 👉 parent_proxy_type.name 👈::👉proxy_field.variable_builder_name 👈(👉 operation_pointer 👈)
{% endif -%}
{% endset -%}
if (!data.value("👉proxy_field.name👈").isNull()){
{% if proxy_field.type.is_queried_object_type -%}
👉 setter_name 👈(👉proxy_field.type.deserializer_name👈(data.value("👉proxy_field.name👈").toObject(), 👉operation_pointer👈) 👉 setter_end 👈);

{% elif proxy_field.type.is_queried_interface or  proxy_field.type.is_queried_union -%}
auto 👉proxy_field.name👈_data = data.value("👉proxy_field.name👈").toObject();
auto 👉proxy_field.name👈_typename  = 👉proxy_field.name👈_data.value("__typename").toString();
{%set type_cond -%}👉proxy_field.name👈_typename{% endset -%}
{% for choice in proxy_field.type.choices -%}
{% set do_on_meets -%}
👉 setter_name 👈(👉choice.deserializer_name👈(👉proxy_field.name👈_data, 👉operation_pointer👈) 👉 setter_end 👈);
{% endset -%}
👉iterate_type_condition(choice,type_cond, do_on_meets, loop)👈
{% endfor %}
{% elif proxy_field.type.is_model -%}
    {% if proxy_field.type.of_type.is_builtin_scalar %}
    std::vector<👉proxy_field.type.of_type.type_name()👈> 👉proxy_field.name👈_init_vec;
    for (const auto& node: data.value("👉proxy_field.name👈").toArray()){
        👉proxy_field.name👈_init_vec.push_back(node.👉 proxy_field.type.of_type.from_json_convertor 👈);
    }
    👉 setter_name 👈(std::make_shared<👉proxy_field.concrete.type.type_name()👈>(nullptr, 👉proxy_field.name👈_init_vec) 👉 setter_end 👈);
    {% else %}
        👉proxy_field.concrete.type.member_type👈 👉proxy_field.name👈_init_vec;
        for (const auto& node: data.value("👉proxy_field.name👈").toArray()){
        {% if proxy_field.type.is_model.of_type.is_queried_object_type %}
            👉proxy_field.name👈_init_vec.push_back(👉 proxy_field.type.of_type.is_queried_object_type.deserializer_name 👈(node.toObject(), 👉operation_pointer👈));
        {% elif proxy_field.type.is_model.of_type.is_queried_union or proxy_field.type.is_model.of_type.is_queried_interface %}
            auto node_data = node.toObject();
            auto 👉proxy_field.name👈_typename = node_data.value("__typename").toString();
            {%set type_cond -%}👉proxy_field.name👈_typename{% endset -%}
            {% for choice in proxy_field.type.of_type.choices -%}
            {% set do_on_meets -%}
            👉proxy_field.name👈_init_vec.push_back(👉choice.deserializer_name👈(node_data, 👉operation_pointer👈) 👉 setter_end 👈);
            {% endset -%}
            👉iterate_type_condition(choice,type_cond, do_on_meets, loop)👈
            {% endfor %}
        {% else %}
        throw qtgql::exceptions::NotImplementedError({"can't deserialize model of 👉proxy_field.type.of_type.__class__👈"});
        {% endif %}
        };
        👉 setter_name 👈(👉proxy_field.name👈_init_vec 👉 setter_end 👈);
    {% endif %}
{% elif proxy_field.type.is_builtin_scalar -%}
    {% if proxy_field.type.is_void -%}
    /* deliberately empty */
    {% else -%}
    👉 setter_name 👈(std::make_shared<👉proxy_field.type.type_name()👈>(data.value("👉proxy_field.name👈").👉 proxy_field.type.is_builtin_scalar.from_json_convertor 👈) 👉 setter_end 👈);
    {% endif %}
    {% elif proxy_field.type.is_custom_scalar -%}
    auto new_👉proxy_field.name👈 = std::make_shared<👉 proxy_field.type.is_custom_scalar.type_name() 👈>();
    new_👉proxy_field.name👈->deserialize(data.value("👉proxy_field.name👈"));
    👉 setter_name 👈(new_👉proxy_field.name👈 👉 setter_end 👈);
{% elif proxy_field.type.is_enum -%}
👉 setter_name 👈(std::make_shared<👉proxy_field.type.namespaced_name👈>(Enums::👉proxy_field.type.is_enum.map_name👈::by_name(data.value("👉proxy_field.name👈").toString()))👉 setter_end 👈);
{% endif -%} 👉 do_after_deserialized 👈
};
{%- endmacro %}
