{% import "macros.jinja.hpp" as macros -%}
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

👉 macros.concrete_type_fields(interface) 👈

{% if interface.is_node_interface -%}
static auto & ENV_CACHE() {
        static auto cache = qtgql::bases::Environment::get_env_strict("👉 context.config.env_name 👈")->get_cache();
        return cache;
}
{% endif %}

static std::shared_ptr<👉 interface.name 👈> from_json(const QJsonObject& data,
                                                const qtgql::bases::SelectionsConfig &config,
                                                const qtgql::bases::OperationMetadata& metadata);

};
{% endfor %}

// ---------- Object Types ----------
{% for type in context.types %}
{%- set base_class -%}{% if type. implements_node %}NodeInterfaceABC{% else %}ObjectTypeABC{% endif %}{%- endset -%}
class 👉 type.name 👈 {% for base in type.bases %}{%if loop.first%}: {% endif %} public 👉 base.name 👈 {% if not loop.last %}, {% endif %}{% endfor %}{
Q_OBJECT

👉 macros.concrete_type_fields(type) 👈
public:

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

static std::shared_ptr<👉 type.name 👈> from_json(const QJsonObject& data,
                                 const qtgql::bases::SelectionsConfig &config,
                                 const qtgql::bases::OperationMetadata& metadata){
if (data.isEmpty()){
    return {};
}
{% if type. implements_node %}
if (config.selections.contains("id") && !data.value("id").isNull()) {
    auto cached_maybe = get_node(data.value("id").toString());
    if(cached_maybe.has_value()){
        auto node = cached_maybe.value();
        node->update(data, config, metadata);
        return node;
    }
};
{% endif %}

auto inst = std::make_shared<👉 type.name 👈>();
{% for f in type.fields -%}
{% set assign_to %} inst->👉 f.private_name 👈 {% endset %}
👉macros.deserialize_field(f, assign_to)👈
{% endfor %}
{% if type. implements_node %}
ENV_CACHE()->add_node(inst);
{% endif %}
return inst;
};

void update(const QJsonObject &data,
            const qtgql::bases::SelectionsConfig &config,
            const qtgql::bases::OperationMetadata &metadata)
            {
            {%for f in type.fields -%}
            {% set fset %}👉f.setter_name👈{% endset %}{% set private_name %}👉f.private_name👈{% endset -%}
            👉 macros.update_concrete_field(f, fset_name=fset, private_name=private_name) 👈
            {% endfor %}
};

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
std::optional<👉f.member_type👈> 👉f.name👈 = {};
{% endfor -%}
👉type.name👈(QObject* parent, {% for f in type.fields %} std::optional<👉f.member_type👈> &👉f.name👈{% if not loop.last %},{% endif %} {% endfor %}): QObject::QObject(parent){
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