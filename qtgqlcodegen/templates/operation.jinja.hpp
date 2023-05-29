{% import "macros.jinja.hpp" as macros -%}
#pragma once
#include "./schema.hpp"
#include <qtgql/gqlwstransport/gqlwstransport.hpp>
#include <QObject>

namespace 👉 context.config.env_name 👈{
namespace 👉context.ns👈{
const auto OPERATION_ID = QUuid::fromString("👉 context.operation.operation_id👈");

{% for t in context.operation.narrowed_types %}
class 👉 t.name 👈: public QObject{
/*
👉 t.doc_fields 👈
 */
    Q_OBJECT
{# members #}
std::shared_ptr<👉context.schema_ns👈::👉 t.definition.name 👈> m_inst;
{% for ref in t.references -%}
std::unique_ptr<👉ref.narrowed_type.name👈> m_👉ref.name👈;
{% endfor %}
{%- for model_field in t.models -%}
std::unique_ptr<👉 model_field.property_type 👈> m_👉model_field.name👈;
{% endfor %}

public:
👉 t.name 👈(const std::shared_ptr<👉 t.definition.name 👈> &inst ): m_inst{inst}, QObject::QObject(nullptr){
{% for ref in t.references -%}
{% if ref.type.is_optional() %}
if (m_inst->👉ref.definition.getter_name 👈()){
m_👉ref.name👈 = std::make_unique<👉ref.narrowed_type.name👈>(m_inst->👉ref.definition.getter_name 👈());
}
else{
m_👉ref.name👈 = std::unique_ptr<👉ref.narrowed_type.name👈>();
}
{% else %}
m_👉ref.name👈 = std::make_unique<👉ref.narrowed_type.name👈>(m_inst->👉ref.definition.getter_name 👈());
{% endif %}
{% endfor %}
{%- for model_field in t.models -%}
auto init_vec_👉 model_field.name 👈 =  std::make_unique<std::vector<std::unique_ptr<👉model_field.narrowed_type.name👈>>>();
for (const auto & node: m_inst->👉model_field.definition.getter_name 👈().value(OPERATION_ID)){
    init_vec_👉 model_field.name 👈->push_back(std::move(std::make_unique<👉model_field.narrowed_type.name👈>(node)));
}
m_👉model_field.name👈 = std::make_unique<👉 model_field.property_type 👈>(nullptr, std::move(init_vec_👉 model_field.name 👈));
{% endfor -%}
}
{%- for f in t.fields.values() %}
{% if f.type.is_optional() and f.type.is_object_type %}
[[nodiscard]] inline const 👉 f.property_type 👈 * 👉 f.definition.getter_name 👈() const {
    return m_👉f.name👈.get();
{% else %}
[[nodiscard]] inline const 👉 f.property_type 👈 & 👉 f.definition.getter_name 👈() const {
    {% if f.type.is_object_type or f.type.is_model %}
    return *m_👉f.name👈;
    {% else %}
    return m_inst->👉 f.definition.getter_name 👈();
    {% endif %}
{% endif %}
};
{% endfor -%}
};
{% endfor %}

class 👉 context.operation.name 👈: public qtgql::gqlwstransport::OperationHandlerABC {
    Q_OBJECT
Q_PROPERTY(const 👉 context.operation.root_field.property_type 👈* data READ get_data NOTIFY dataChanged);

std::unique_ptr<👉 context.operation.root_field.property_type 👈> m_data;

inline const QString &ENV_NAME() override{
    static const auto ret = QString("👉 context.config.env_name 👈");
    return ret;
    }

inline const qtgql::bases::OperationMetadata & OPERATION_METADATA() override{
auto static ret = qtgql::bases::OperationMetadata{
        OPERATION_ID,
        {👉 context.operation.root_field.as_conf_string() 👈}
};
return ret;
};
public:
👉 context.operation.name 👈(): qtgql::gqlwstransport::OperationHandlerABC(qtgql::gqlwstransport::GqlWsTrnsMsgWithID(qtgql::gqlwstransport::OperationPayload(
        {%- for line in context.operation.query.splitlines() %}"👉 line 👈"{% endfor -%}
        ))){};

inline const QUuid &operation_id() const override{
return OPERATION_ID;
}


void on_next(const QJsonObject &message) override{
    if (!m_data && message.contains("data")){
        auto data = message.value("data").toObject();
        if (data.contains("👉 context.operation.root_field.name 👈")){
            m_data = std::make_unique<👉 context.operation.root_field.property_type 👈>(
👉context.schema_ns👈::👉 context.operation.root_field.definition.type.is_object_type.name 👈::from_json(
        data.value("👉 context.operation.root_field.name 👈").toObject(), OPERATION_METADATA().selections, OPERATION_METADATA())
);
        }
    }
}
inline const 👉 context.operation.root_field.property_type 👈* get_data(){
    return m_data.get();
}

{% if context.operation.variables %}
void setVariables(
{% for var in context.operation.variables -%}
const std::optional<👉 var.type.member_type 👈>  👉 var.name 👈 {% if not loop.last %},{% endif %}
{% endfor -%}){
{% for var in context.operation.variables %}
if (👉 var.name 👈.has_value()){
    m_variables.insert("👉 var.name 👈",  👉 var.json_repr() 👈);
}
{% endfor %}
}
{% endif %}

signals:
void dataChanged();

};
};
};

