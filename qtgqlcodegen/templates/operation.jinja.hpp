{% import "macros.jinja.hpp" as macros -%}
#pragma once
#include "./schema.hpp"
#include "qtgqloperationhandler.hpp"
namespace 👉context.ns👈{

const qtgql::OperationMetadata OPERATION_METADATA = qtgql::OperationMetadata{
        "👉 context.operation.name 👈",
        {
                👉 context.operation.root_field.as_conf_string() 👈
        }
};


{% for t in context.operation.narrowed_types %}
class 👉 t.name 👈{
/*
👉 t.doc_fields 👈
 */
    Q_GADGET
std::shared_ptr<👉context.schema_ns👈::👉 t.definition.name 👈> m_inst;

public:

👉 t.name 👈(const QJsonObject& data,
const qtgql::SelectionsConfig& config){
    m_inst = 👉context.schema_ns👈::👉 t.definition.name 👈::from_json(data, config, OPERATION_METADATA);

}
{%- for f in t.fields.values() %}
const 👉 f.type.annotation 👈 & 👉 f.definition.getter_name 👈() const {
    return m_inst->👉 f.definition.getter_name 👈();
};
{% endfor -%}
};
{% endfor %}

class 👉 context.operation.name 👈: qtgql::QtGqlOperationHandlerABC {
    Q_OBJECT
Q_PROPERTY(👉 context.operation.root_field.property_annotation 👈 data MEMBER m_data NOTIFY dataChanged);

std::unique_ptr<👉 context.operation.root_field.property_annotation 👈> m_data;

const QString &ENV_NAME() override{
    static const auto ret = QString("👉 context.config.env_name 👈");
    return ret;
    }
public:
const QUuid &operation_id() const override{
return m_message_template.op_id;
}


void on_next(const QJsonObject &message) override{
    if (!m_data){
        m_data = std::make_unique<👉 context.operation.root_field.property_annotation 👈>(message, OPERATION_METADATA.selections);
    }
}
};


};

