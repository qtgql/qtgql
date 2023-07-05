{%- from "macros/concrete_type_fields.jinja.hpp" import concrete_type_fields -%}
#pragma once
#include <QObject>
#include <QJsonObject>
#include <QJsonArray>
#include <memory>

#include <qtgql/bases/bases.hpp>
{% for dep in context.dependencies -%}
👉 dep 👈
{% endfor %}

namespace 👉 context.config.env_name 👈{
{% if context.enums %}
// ---------- Enums ----------

class Enums{
    Q_GADGET

public:
{% for enum in context.enums %}
enum 👉enum.name👈{
{% for member in enum.members -%}
👉member.name👈 = 👉member.index👈,
{% endfor %}
};
Q_ENUM(👉enum.name👈)
struct 👉enum.map_name👈{
Q_GADGET
public:
inline static const std::vector<std::pair<QString, 👉enum.name👈>> members = {
        {% for member in enum.members -%}
        {"👉member.name👈", 👉enum.name👈::👉member.name👈},
        {% endfor %}
};
    GraphQLEnum_MACRO(👉enum.name👈)
};

{% endfor %}
};
{% endif %}

// ---------- INPUT OBJECTS ----------
{% for type in context.input_objects -%}
/*
 * 👉 type.docstring 👈
 */
struct 👉type.name👈{

public:
{# // this is doubtfully needed, but std::map requires comparison for ordering. #}
bool operator<(const 👉type.name👈& other) const {
    {% for f in type.fields -%}
    if(👉f.name👈 < other.👉f.name👈){
        return true;
    }
    {% endfor -%}
    return false;
}
{% for f in type.fields -%}
std::optional<👉f.type.member_type👈> 👉f.name👈 = {};
{% endfor %}
[[nodiscard]] QJsonObject to_json() const{
    auto ret = QJsonObject();
    {% for f in type.fields %}{% set attr_name %}👉f.name👈{% endset %}
    if (👉attr_name👈.has_value()){
        ret.insert("👉f.name👈", 👉f.json_repr(attr_name)👈);
    }
    {% endfor %}
    return ret;
}
};
{% endfor %}

// ---------- Interfaces ----------
{% for interface in context.interfaces -%}
class 👉 interface.name 👈 {% for base in interface.bases %} {%if loop.first %}: {% endif %} public 👉 base.name 👈 {% if not loop.last %}, {% endif %}{% endfor %}{
Q_OBJECT

👉 concrete_type_fields(interface) 👈

{% if interface.is_node_interface -%}
static auto & ENV_CACHE() {
        static auto cache = qtgql::bases::Environment::get_env_strict("👉 context.config.env_name 👈")->get_cache();
        return cache;
}
{% endif %}
};
{% endfor %}

// ---------- Object Types ----------
{# forward references -#}
{% for type in context.types -%}
class 👉 type.name 👈;
{% endfor %}

{% for type in context.types %}
{%- set base_class -%}{% if type. implements_node %}NodeInterfaceABC{% else %}ObjectTypeABC{% endif %}{%- endset -%}
class 👉 type.name 👈 {% for base in type.bases %}{%if loop.first%}: {% endif %} public 👉 base.name 👈 {% if not loop.last %}, {% endif %}{% endfor %}{
Q_OBJECT
👉 concrete_type_fields(type) 👈
public:
{% if type.is_root %} {# root types should be singletons #}
[[nodiscard]] static 👉 type.name 👈* instance(){
static 👉 type.name 👈 inst;
return &inst;
}
{% else %}
QTGQL_STATIC_MAKE_SHARED(👉 type.name 👈)
{% endif %}

👉 type.name 👈()= default;

public:
inline const QString & __typename() const final{
static const QString ret = "👉 type.name 👈";
return ret;
};
};
{% endfor %}

}