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
👉ref.narrowed_type.name👈 * m_👉ref.name👈;
{% endfor %}
{%- for model_field in t.models -%}
👉 model_field.property_type 👈* m_👉model_field.name👈;
{% endfor %}

public:
👉 t.name 👈(QObject* parent, const std::shared_ptr<👉 t.definition.name 👈> &inst ): m_inst{inst}, QObject::QObject(parent){
{% for ref in t.references -%}
{% if ref.type.is_optional() %}
if (m_inst->👉ref.definition.getter_name 👈()){
m_👉ref.name👈 = new 👉ref.narrowed_type.name👈(this, m_inst->👉ref.definition.getter_name 👈());
}
else{
m_👉ref.name👈 = nullptr;
}
{% else %}
m_👉ref.name👈 = new 👉ref.narrowed_type.name👈(this, m_inst->👉ref.definition.getter_name 👈());
{% endif %}
{% endfor %}
{%- for model_field in t.models -%}
auto init_list_👉 model_field.name 👈 =  std::make_unique<QList<👉model_field.narrowed_type.name👈*>>();
for (const auto & node: m_inst->👉model_field.definition.getter_name 👈().value(OPERATION_ID)){
    init_list_👉 model_field.name 👈->append(new 👉model_field.narrowed_type.name👈(this, node));
}
m_👉model_field.name👈 = new 👉 model_field.property_type 👈(this, std::move(init_list_👉 model_field.name 👈));
{% endfor -%}
}
{%- for f in t.fields.values() %}
{% if f.type.is_object_type or f.type.is_model %}
[[nodiscard]] inline const 👉 f.property_type 👈 * 👉 f.definition.getter_name 👈() const {
    return m_👉f.name👈;
{% else %}
[[nodiscard]] inline const 👉 f.property_type 👈 & 👉 f.definition.getter_name 👈() const {
    {% if f.type.is_object_type %}
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

👉 context.operation.root_field.property_type 👈 *m_data;

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
        ), OPERATION_ID)){};

inline const QUuid &operation_id() const override{
return OPERATION_ID;
}


void on_next(const QJsonObject &message) override{
    if (!m_data && message.contains("data")){
        auto data = message.value("data").toObject();
        if (data.contains("👉 context.operation.root_field.name 👈")){
            m_data = new 👉 context.operation.root_field.property_type 👈(this,
👉context.schema_ns👈::👉 context.operation.root_field.definition.type.is_object_type.name 👈::from_json(
        data.value("👉 context.operation.root_field.name 👈").toObject(), OPERATION_METADATA().selections, OPERATION_METADATA())
);
        }
    }
}
inline const 👉 context.operation.root_field.property_type 👈* get_data(){
    return m_data;
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

