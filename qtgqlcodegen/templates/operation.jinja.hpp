{% import "macros.jinja.hpp" as macros -%}
#pragma once
#include "./schema.hpp"
#include <qtgql/gqlwstransport/gqlwstransport.hpp>

namespace 👉 context.config.env_name 👈{
namespace 👉context.ns👈{

inline const qtgql::bases::OperationMetadata OPERATION_METADATA = qtgql::bases::OperationMetadata{
        "👉 context.operation.name 👈",
        {👉 context.operation.root_field.as_conf_string() 👈}
};


{% for t in context.operation.narrowed_types %}
class 👉 t.name 👈{
/*
👉 t.doc_fields 👈
 */
    Q_GADGET
std::shared_ptr<👉context.schema_ns👈::👉 t.definition.name 👈> m_inst;
{% for ref in t.references -%}
std::unique_ptr<👉ref.narrowed_type.name👈> m_👉ref.name👈;
{% endfor %}

public:
👉 t.name 👈(const std::shared_ptr<👉 t.definition.name 👈> inst ): m_inst{inst}{
{% for ref in t.references -%}
m_👉ref.name👈 = std::make_unique<👉ref.narrowed_type.name👈>(m_inst->👉ref.definition.getter_name 👈());
{% endfor %}
}
{%- for f in t.fields.values() %}
[[nodiscard]] inline const 👉 f.property_type 👈 & 👉 f.definition.getter_name 👈() const {
    {% if f.type.is_object_type %}
    return *m_👉f.name👈;
    {% else %}
    return m_inst->👉 f.definition.getter_name 👈();
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
public:

👉 context.operation.name 👈(): qtgql::gqlwstransport::OperationHandlerABC(qtgql::gqlwstransport::GqlWsTrnsMsgWithID(qtgql::gqlwstransport::OperationPayload(
        {%- for line in context.operation.query.splitlines() %}"👉 line 👈"{% endfor -%}
        ))){};

inline const QUuid &operation_id() const override{
return m_message_template.op_id;
}


void on_next(const QJsonObject &message) override{
    if (!m_data && message.contains("data")){
        auto data = message.value("data").toObject();
        if (data.contains("👉 context.operation.root_field.name 👈")){
            m_data = std::make_unique<👉 context.operation.root_field.property_type 👈>(
👉context.schema_ns👈::👉 context.operation.root_field.definition.type.is_object_type.name 👈::from_json(
        data.value("👉 context.operation.root_field.name 👈").toObject(), OPERATION_METADATA.selections, OPERATION_METADATA)
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

