{%- from "macros/initialize_proxy_field.jinja.hpp" import initialize_proxy_field -%}
{%- from "macros/deserialize_concrete_field.jinja.hpp" import  deserialize_concrete_field -%}
#pragma once
#include "./schema.hpp"
#include <qtgql/gqlwstransport/gqlwstransport.hpp>
#include <QObject>

namespace 👉 context.config.env_name 👈::👉context.ns👈{
class 👉 context.operation.name 👈;

namespace deserializers{
{% for t in context.operation.narrowed_types -%}
std::shared_ptr<👉 t.concrete.name 👈> des_👉 t.name 👈(const QJsonObject& data, const 👉 context.operation.name 👈 * operation);
{% endfor -%}
{% for t in context.operation.interfaces -%}
std::shared_ptr<👉 t.concrete.name 👈> des_👉 t.name 👈(const QJsonObject& data, const 👉 context.operation.name 👈 * operation);
{% endfor -%}
};

namespace updaters{
{% for t in context.operation.narrowed_types -%}
void update_👉 t.name 👈(👉 t.concrete.member_type 👈 &inst, const QJsonObject &data, const 👉 context.operation.name 👈 * operation);
{% endfor -%}

};

// ------------ Narrowed Object types ------------
{% for t in context.operation.narrowed_types %}
class 👉 t.name 👈: public QObject{
/*
👉 t.doc_fields 👈
 */
    Q_OBJECT
{% for f in t.fields -%}
Q_PROPERTY(const 👉 f.property_type 👈 👉 f.name 👈 READ 👉 f.concrete.getter_name 👈 NOTIFY 👉 f.concrete.signal_name 👈);
{% endfor %}
signals:
{%for f in t.fields -%}
void 👉 f.concrete.signal_name 👈();
{% endfor %}

{# members #}
{% if context.debug -%}
public: // WARNING: members are public because you have debug=True in your config file.
{% else %}
protected:
{% endif %}
const std::shared_ptr<👉context.schema_ns👈::👉 t.concrete.name 👈> m_inst;
{% for ref_field in t.references -%}
const 👉ref_field.property_type👈 m_👉ref_field.name👈 = {};
{% endfor %}
{%- for model_field in t.models -%}
👉 model_field.property_type 👈 m_👉model_field.name👈;
{% endfor %}

public:
👉 t.name 👈(👉 context.operation.name 👈 * operation, const std::shared_ptr<👉 t.concrete.name 👈> &inst);

{% for f in t.fields -%}
{%- if f.type.is_queried_object_type or f.type.is_model %}
[[nodiscard]] inline const 👉 f.property_type 👈  👉 f.concrete.getter_name 👈() const {
    return m_👉f.name👈;
{%- else -%}
{#- TODO: find a better way to pass the object to QML -#}
[[nodiscard]] inline const 👉 f.property_type 👈 👉 f.concrete.getter_name 👈() const {
    {# TODO: is that require? -#}
    {% if f.type.is_queried_object_type -%}
    return *m_👉f.name👈;
    {% else -%}
    return m_inst->👉 f.concrete.getter_name 👈();
    {% endif -%}
{%- endif -%}
};
{% endfor -%}
};
{% endfor %}

struct 👉 context.operation.generated_variables_type 👈{
{% for var in context.operation.variables -%}
std::optional<👉 var.type.member_type 👈> 👉 var.name 👈 = {};
{% endfor -%}

    QJsonObject to_json() const{
    QJsonObject ret;
    {% for var in context.operation.variables -%}
    if (👉 var.name 👈.has_value()){
    ret.insert("👉 var.name 👈",  👉 var.json_repr() 👈);
    }
    {% endfor -%}
    return ret;
    }
};

class 👉 context.operation.name 👈: public qtgql::gqlwstransport::OperationHandlerABC{
    Q_OBJECT
Q_PROPERTY(const 👉 context.operation.root_field.property_type 👈 data READ 👉 context.operation.root_field.concrete.getter_name 👈 NOTIFY 👉 context.operation.root_field.concrete.signal_name 👈);

std::optional<👉 context.operation.root_field.property_type 👈> 👉 context.operation.root_field.private_name 👈 = {};



inline const QString &ENV_NAME() override{
    static const auto ret = QString("👉 context.config.env_name 👈");
    return ret;
    }


public:
👉 context.operation.generated_variables_type 👈 vars_inst;

👉 context.operation.name 👈(): qtgql::gqlwstransport::OperationHandlerABC(qtgql::gqlwstransport::GqlWsTrnsMsgWithID(qtgql::gqlwstransport::OperationPayload(
        {%- for line in context.operation.query.splitlines() %}"👉 line 👈"{% endfor -%}
        ))){
m_message_template.op_id = m_operation_id;
};


QTGQL_STATIC_MAKE_SHARED(👉 context.operation.name 👈)

inline const QUuid & operation_id() const override{
return m_operation_id;
}


void on_next(const QJsonObject &message) override{
    if (!👉 context.operation.root_field.private_name 👈  && message.contains("data")){
        auto data = message.value("data").toObject();
        {% set do_after_deserialized -%}
        👉 initialize_proxy_field(context.operation.root_field, operation_pointer="this") 👈
        {%- endset -%}
        👉 deserialize_concrete_field(context.operation.root_field,  "auto concrete", "this", do_after_deserialized) 👈
    }
}
inline const 👉 context.operation.root_field.property_type 👈 👉 context.operation.root_field.concrete.getter_name 👈() const{
    return 👉 context.operation.root_field.concrete.private_name 👈.value();
}

{% if context.operation.variables %}
void set_variables(👉 context.operation.generated_variables_type 👈 vars){
vars_inst = vars;
m_variables = vars_inst.to_json();
}
{% endif %}

signals:
void 👉 context.operation.root_field.concrete.signal_name 👈();

};
};

