{% import "macros.jinja.hpp" as macros -%}
#pragma once
#include "./schema.hpp"
#include "qtgqloperationhandler.hpp"
namespace 👉 context.config.env_name 👈{
namespace 👉context.ns👈{

inline const qtgql::OperationMetadata OPERATION_METADATA = qtgql::OperationMetadata{
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
inline const 👉 f.type.annotation 👈 & 👉 f.definition.getter_name 👈() const {
    return m_inst->👉 f.definition.getter_name 👈();
};
{% endfor -%}
};
{% endfor %}

class 👉 context.operation.name 👈: public qtgql::QtGqlOperationHandlerABC {
    Q_OBJECT
Q_PROPERTY(const 👉 context.operation.root_field.property_annotation 👈* data READ get_data NOTIFY dataChanged);

std::unique_ptr<👉 context.operation.root_field.property_annotation 👈> m_data;

inline const QString &ENV_NAME() override{
    static const auto ret = QString("👉 context.config.env_name 👈");
    return ret;
    }
public:

👉 context.operation.name 👈(): qtgql::QtGqlOperationHandlerABC(qtgql::GqlWsTrnsMsgWithID(qtgql::OperationPayload(
        {%- for line in context.operation.query.splitlines() %}"👉 line 👈"{% endfor -%}
        ))){};

inline const QUuid &operation_id() const override{
return m_message_template.op_id;
}


void on_next(const QJsonObject &message) override{
    if (!m_data && message.contains("data")){
        auto data = message.value("data").toObject();
        if (data.contains("👉 context.operation.root_field.name 👈")){
            m_data = std::make_unique<👉 context.operation.root_field.property_annotation 👈>(data.value("👉 context.operation.root_field.name 👈").toObject(), OPERATION_METADATA.selections);
        }
    }
}
inline const 👉 context.operation.root_field.property_annotation 👈* get_data(){
    return m_data.get();
}

signals:
    void dataChanged();
};
};
};

