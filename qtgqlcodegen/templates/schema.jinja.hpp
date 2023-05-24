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

// ----------- Object Types -----------
{% for type in context.types %}
{%- set base_class -%}{% if type.has_id_field %}ObjectTypeABCWithID{% else %}ObjectTypeABC{% endif %}{%- endset -%}
class 👉 type.name 👈 : public qtgql::bases::👉 base_class 👈{
protected:
static auto & INST_STORE() {
    static qtgql::bases::ObjectStore<👉 type.name 👈> _store;
    return _store;
}

👉 macros.props(type) 👈
public:
inline static const QString TYPE_NAME = "👉 type.name 👈";
👉 type.name 👈 (QObject* parent = nullptr)
: qtgql::bases::👉 base_class 👈::👉 base_class 👈(parent) {};


static std::shared_ptr<👉 type.name 👈> from_json(const QJsonObject& data,
                                 const qtgql::bases::SelectionsConfig& config,
                                 const qtgql::bases::OperationMetadata& metadata){
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
record->retain(metadata.operation_name);
INST_STORE().add_record(record);
{% endif %}
return inst;
  };
{% endfor %}

void loose(const qtgql::bases::OperationMetadata &metadata){throw "not implemented";};
void update(const QJsonObject &data,
            const qtgql::bases::SelectionsConfig &selections){throw "not implemented";};

};

}