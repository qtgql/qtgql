{% import "macros.jinja.cpp" as macros -%}
#pragma once
#include <QObject>
#include <QJsonObject>
#include <memory>
#include <qtgqlobjecttype.hpp>
#include <qtgqlmetadata.hpp>
#include <qtgqlconstants.hpp>
namespace 👉context.config.env_name👈{
{% macro init_and_props(type) %}
protected:

{% for f in type.fields -%}
👉f.annotation👈 👉f.private_name👈 = 👉f.default_value👈;
{% endfor %}

public:
👉type.name👈 (QObject* parent = nullptr)
    : QObject::QObject(parent) {};

signals:
{%for f in type.fields -%}
void 👉f.signal_name👈();
{% endfor %}

public:
{%for f in type.fields %}
void 👉f.setter_name👈(const 👉f.annotation👈 &v)
{
  👉f.private_name👈 = v;
  emit 👉f.signal_name👈();
};
{% endfor %}
{% endmacro %}
// ----------- Object Types -----------
{% for type in context.types %}
class 👉 type.name 👈 : public {% if type.has_id_field %}
qtgql::QtGqlObjectTypeABC {% else %} qtgql::QtGqlObjectTypeWithIdABC{% endif %}{

inline static const QString TYPE_NAME = "👉type.name👈";
👉init_and_props(type)👈

public:
std::shared_ptr<👉type.name👈> from_json(QObject * parent, const QJsonObject& data,
                                 const qtgql::SelectionsConfig& config,
                                 const qtgql::OperationMetadata& metadata){
auto inst = std::make_shared<👉type.name👈>();
{% for f in type.fields -%}
{% set assign_to %} inst->👉f.private_name👈 {% endset %}
👉macros.deserialize_field(f, assign_to)👈
{% endfor %}
{% if type.id_is_optional %}
if (inst->id) {
  auto record = NodeRecord(node = inst, retainers = set())
                    .retain(metadata.operation_name)
                        cls.__store__.add_record(record)
}
{% elif type.has_id_field and not type.id_is_optional %} record =
    NodeRecord(node = inst, retainers = set())
        .retain(metadata.operation_name);
    cls.__store__.add_record(record); 
{% endif %}
return inst;
  };
  
};
{% endfor %}
}