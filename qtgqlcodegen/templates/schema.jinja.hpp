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
{% for type in context.types -%} {# forward references -#}
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

inline static const QString TYPE_NAME = "👉 type.name 👈";

{% if type.implements_node -%}
static std::optional<std::shared_ptr<👉 type.name 👈>> get_node(const QString & id){
    auto node = ENV_CACHE()->get_node(id);
    if (node.has_value()){
        return std::static_pointer_cast<👉 type.name 👈>(node.value());
    }
    return {};
}
{% endif %}
};
{% endfor %}

// ---------- INPUT OBJECTS ----------

{% for type in context.input_objects %}
/*
 * 👉 type.docstring 👈
 */
struct 👉type.name👈: QObject{
Q_OBJECT

public:
{% for f in type.fields %}
std::optional<👉f.type.member_type👈> 👉f.name👈 = {};
{% endfor -%}
👉type.name👈(QObject* parent, {% for f in type.fields %} std::optional<👉f.type.member_type👈> &👉f.name👈{% if not loop.last %},{% endif %} {% endfor %}): QObject::QObject(parent){
    {% for f in type.fields -%}
    👉f.name👈 = 👉f.name👈;
    {% endfor %}
};
QJsonObject to_json() const{
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

}