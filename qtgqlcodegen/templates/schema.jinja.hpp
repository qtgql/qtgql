{%- from "macros/concrete_type_fields.jinja.hpp" import concrete_type_fields -%}
{%- from "macros/serialize_input_variable.jinja.hpp" import  serialize_input_variable -%}
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
{% for arg in type.fields -%}
{% if arg.type.is_optional -%}
std::optional<👉 arg.type.type_name() 👈> 👉 arg.name 👈 = {};
{% else -%}
👉 arg.type.type_name() 👈 👉 arg.name 👈;
{% endif -%}
{% endfor -%}
[[nodiscard]] QJsonObject to_json() const{
    auto __ret = QJsonObject();
    {% for arg in type.fields -%}
    👉serialize_input_variable("__ret", arg, attr_name=arg.name, json_name=arg.name)👈
    {% endfor -%}
    return __ret;
}

template<typename... Args>
static 👉type.type_name()👈 create(Args... args){
    return std::make_shared<👉type.name👈>(args...);
}


};
{% endfor %}

// Forward references
{% for type in context.types -%}
class 👉 type.name 👈;
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

{% for type in context.types %}
{%- set base_class -%}{% if type. implements_node %}NodeInterfaceABC{% else %}ObjectTypeABC{% endif %}{%- endset -%}
class 👉 type.name 👈 {% for base in type.bases %}{%if loop.first%}: {% endif %} public 👉 base.name 👈 {% if not loop.last %}, {% endif %}{% endfor %}{
Q_OBJECT
👉 concrete_type_fields(type) 👈
public:
{% if type.is_root %} {# root types should be singletons #}
[[nodiscard]] static std::shared_ptr<👉 type.name 👈> instance(){
    static std::weak_ptr<👉 type.name 👈> observer_inst;
    if (observer_inst.expired()){
        auto ret = std::make_shared<👉 type.name 👈>();
        observer_inst = ret;
        return ret;
    }
    return observer_inst.lock();
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