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
{% for f in t.fields -%}
Q_PROPERTY(const 👉 f.property_type 👈 👉 f.name 👈 READ 👉 f.definition.getter_name 👈 NOTIFY 👉 f.definition.signal_name 👈);
{% endfor %}
signals:
{%for f in t.fields -%}
void 👉 f.definition.signal_name 👈();
{% endfor %}

{# members #}
{% if context.debug -%}
public: // WARNING: members are public because you have debug=True in your config file.
{% else %}
protected:
{% endif %}
std::shared_ptr<👉context.schema_ns👈::👉 t.definition.name 👈> m_inst;
{% for ref_field in t.references -%}
👉ref_field.property_type👈 m_👉ref_field.name👈 = {};
{% endfor %}
{%- for model_field in t.models -%}
👉 model_field.property_type 👈 m_👉model_field.name👈;
{% endfor %}

public:
👉 t.name 👈(QObject* parent, const std::shared_ptr<👉 t.definition.name 👈> &inst ): m_inst{inst}, QObject::QObject(parent){
{% for field in t.fields -%}
👉 macros.initialize_proxy_field(field) 👈
{# updates logic -#}
connect(m_inst.get(), &👉context.schema_ns👈::👉t.definition.name👈::👉 field.definition.signal_name 👈, this,
        [&](){emit 👉 field.definition.signal_name 👈();});
{% endfor %}
}
{%- for f in t.fields %}
{% if f.type.is_object_type or f.type.is_model %}
[[nodiscard]] inline const 👉 f.property_type 👈  👉 f.definition.getter_name 👈() const {
    return m_👉f.name👈;
{% else %}
{# TODO: this is probably redundan #}
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
Q_PROPERTY(const 👉 context.operation.root_field.property_type 👈 data READ get_data NOTIFY dataChanged);

std::optional<👉 context.operation.root_field.property_type 👈> m_data = {};



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
        if (data.contains("👉 context.operation.root_field.definition.name 👈")){
{%- set do_after_deserialized -%} 👉 macros.initialize_proxy_field(context.operation.root_field) 👈 {% endset -%}
            👉 macros.deserialize_field(context.operation.root_field.definition,
                                    "auto concrete", False,
                                    "OPERATION_METADATA().selections",
                                    "OPERATION_METADATA()",
                                    do_after_deserialized,
                                    ) 👈
        // initialize proxy

        }
    }
}
inline const 👉 context.operation.root_field.property_type 👈 get_data(){
    return m_data.value();
}
inline void loose(){
    {% if context.operation.root_field.type.is_object_type %}
    👉 context.operation.root_field.type.is_object_type.name 👈::INST_STORE().get_node(m_data.value()->get_id()).value()->loose(OPERATION_METADATA());
    {% else %}
    throw "not implemented";
    {% endif %}
}

{% if context.operation.variables %}
void set_variables(
{% for var in context.operation.variables -%}
const std::optional<👉 var.type.type_name 👈> & 👉 var.name 👈 {% if not loop.last %},{% endif %}
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

