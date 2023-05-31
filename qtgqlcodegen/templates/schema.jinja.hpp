{% import "macros.jinja.hpp" as macros -%}
#pragma once
#include <QObject>
#include <QJsonObject>
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
inline static const QString name_by_value(👉enum.name👈 v) {
    for (const auto &member: members) {
        if (member.second == v) { return member.first; }
    }
    throw std::runtime_error("Couldn't find enum member");
};
inline static 👉enum.name👈 by_name(const QString &name) {
    for (const auto &member: members) {
        if (member.first == name) { return member.second; }
    }
    throw std::runtime_error("Couldn't find enum member");
    };
};

{% endfor %}
};
{% endif %}

// ---------- Object Types ----------
{% for type in context.types %}
{%- set base_class -%}{% if type.has_id_field %}ObjectTypeABCWithID{% else %}ObjectTypeABC{% endif %}{%- endset -%}
class 👉 type.name 👈 : public qtgql::bases::👉 base_class 👈{
Q_OBJECT
protected:
static auto & INST_STORE() {
    static qtgql::bases::ObjectStore<👉 type.name 👈> _store;
    return _store;
}

👉 macros.concrete_type_fields(type) 👈
public:
inline static const QString TYPE_NAME = "👉 type.name 👈";

explicit 👉 type.name 👈 (QObject* parent = nullptr)
: qtgql::bases::👉 base_class 👈::👉 base_class 👈(parent) {};


static std::shared_ptr<👉 type.name 👈> from_json(const QJsonObject& data,
                                 const qtgql::bases::SelectionsConfig &config,
                                 const qtgql::bases::OperationMetadata& metadata){
if (data.isEmpty()){
    return {};
}
auto inst = std::make_shared<👉 type.name 👈>();
{% for f in type.fields -%}
{% set assign_to %} inst->👉 f.private_name 👈 {% endset %}
👉macros.deserialize_field(f, assign_to)👈
{% endfor %}
{% if type.id_is_optional %}
if (inst->id) {
  auto record = qtgql::bases::NodeRecord(node = inst, retainers = set())
                    .retain(metadata.operation_name)
                        cls.INST_STORE.add_record(record)
}
{% elif type.has_id_field and not type.id_is_optional %}
auto record = std::make_shared<qtgql::bases::NodeRecord<👉 type.name 👈>>(inst);
record->retain(metadata.operation_id);
INST_STORE().add_record(record);
{% endif %}
return inst;
};

void loose(const qtgql::bases::OperationMetadata &metadata){throw "not implemented";};
void update(const QJsonObject &data,
            const qtgql::bases::SelectionsConfig &selections){throw "not implemented";};

};
{% endfor %}

// ----------------------------------------- INPUT OBJECTS -----------------------------------------

{% for type in context.input_objects %}
/*
 * 👉 type.docstring 👈
 */

struct 👉type.name👈: QObject{
{% for f in type.fields %}
👉f.annotation👈 m_👉f.name👈;
{% endfor -%}

👉type.name👈(QObject* parent, {% for f in type.fields %} 👉f.name👈: 👉f.annotation👈 {% endfor %}): QObject::QObject(parent){
    {% for f in type.fields %}
    m_👉f.name👈 = 👉f.name👈;
    {% endfor -%}
};
QJsonObject to_json(){
    ret = {}
    {% for f in type.fields %}{% set attr_name %}self.👉f.name👈{% endset %}
    if 👉attr_name👈:
    ret['👉f.name👈'] = 👉f.json_repr(attr_name)👈
    {% endfor %}
    return ret
};
}
{% endfor %}

}