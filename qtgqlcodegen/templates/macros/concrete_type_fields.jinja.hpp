{% macro concrete_type_fields(type) -%}
public:
{% for f in type.unique_fields -%}
{% set f_member_type -%}
{% if type.implements_node and f.arguments -%}
std::map<👉f.arguments_type👈, 👉f.type.member_type👈>
{% else -%}
👉f.type.member_type👈
{% endif -%}
{%- endset -%}
👉 f_member_type 👈 👉 f.private_name 👈 = 👉 f.type.default_value 👈;
{% endfor %}
signals:
{%for f in type.unique_fields -%}
void 👉 f.signal_name 👈();
{% endfor %}

public:
{%for f in type.unique_fields %}
[[nodiscard]] const 👉 f.type.fget_type 👈 &👉 f.getter_name 👈(
{%- if f.arguments and type.implements_node -%}👉 f.arguments_type 👈 args {% endif -%}
) {%- if f.type.getter_is_constable -%}const{% endif %}{
{%- if f.arguments and type.implements_node -%}
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
void 👉 f.setter_name 👈(const 👉 f.type.member_type_arg 👈 v {% if f.arguments and type.implements_node %}, 👉 f.arguments_type 👈 args {% endif %})
{
{%- if f.arguments and type.implements_node -%}
{% set f_private_name %}👉 f.private_name 👈[args]{% endset %}
{% else -%}
{% set f_private_name %}👉 f.private_name 👈{% endset %}
{% endif -%}
👉 f_private_name 👈 = v;
emit 👉 f.signal_name 👈();
};
{% endfor %}
{% endmacro -%}

