{% import "macros.jinja.hpp" as macros -%}
#pragma once
#include "./schema.hpp"
#include "qtgqloperationhandler.hpp"
namespace 👉context.ns👈{



{% for t in context.operation.narrowed_types %}
class 👉 t.name 👈{
/*
👉 t.doc_fields 👈
 */
    Q_GADGET
👉context.schema_ns👈::👉 t.definition.name 👈* m_inst;

public:
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

👉 context.operation.root_field.property_annotation 👈 m_data;

const QString &ENV_NAME() override{
    static const auto ret = QString("👉 context.config.env_name 👈");
    return ret;
    }
public:
const QUuid &operation_id() const override{
return m_message_template.op_id;
}

const qtgql::OperationMetadata &OPERATION_METADATA() const override{
static auto ret = qtgql::OperationMetadata{
        "👉 context.operation.name 👈",
        {
                👉 context.operation.root_field.as_conf_string() 👈
        }
};
return ret;
}

};

};

