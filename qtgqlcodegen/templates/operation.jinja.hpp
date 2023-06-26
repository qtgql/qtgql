{%- from "macros/initialize_proxy_field.jinja.hpp" import initialize_proxy_field -%}
{%- from "macros/deserialize_concrete_field.jinja.hpp" import  deserialize_concrete_field -%}
#pragma once
#include "./schema.hpp"
#include <qtgql/gqlwstransport/gqlwstransport.hpp>
#include <QObject>

namespace 👉 context.config.env_name 👈::👉context.ns👈{
class 👉 context.operation.name 👈;

namespace deserializers{
{% for t in context.operation.narrowed_types if not t.concrete.is_root -%}
std::shared_ptr<👉 t.concrete.name 👈> des_👉 t.name 👈(const QJsonObject& data, const 👉 context.operation.name 👈 * operation);
{% endfor -%}
{% for t in context.operation.interfaces -%}
std::shared_ptr<👉 t.concrete.name 👈> des_👉 t.name 👈(const QJsonObject& data, const 👉 context.operation.name 👈 * operation);
{% endfor -%}
};

namespace updaters{
{% for t in context.operation.narrowed_types -%}
void update_👉 t.name 👈(👉 t.concrete.member_type_arg 👈 inst, const QJsonObject &data, const 👉 context.operation.name 👈 * operation);
{% endfor -%}

};

// ------------ Narrowed Object types ------------
{% for t in context.operation.narrowed_types %}
class 👉 t.name 👈: public QObject{
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
{% if t.concrete.is_root %} {# // root types are singletons, no need for shared ptr -#}
👉context.schema_ns👈::👉 t.concrete.name 👈 * m_inst;
{% else %}
const std::shared_ptr<👉context.schema_ns👈::👉 t.concrete.name 👈> m_inst;
{% endif %}
{% for ref_field in t.references -%}
const 👉ref_field.property_type👈 m_👉ref_field.name👈 = {};
{% endfor %}
{%- for model_field in t.models -%}
👉 model_field.property_type 👈 👉model_field.private_name👈;
{% endfor %}

public:
{% if t.concrete.is_root -%}
👉 t.name 👈(👉 context.operation.name 👈 * operation);
{% else -%}
👉 t.name 👈(👉 context.operation.name 👈 * operation, const std::shared_ptr<👉 t.concrete.name 👈> &inst);
{% endif -%}


{% for f in t.fields -%}
{%- if f.type.is_queried_object_type or f.type.is_model %}
[[nodiscard]] inline const 👉 f.property_type 👈  👉 f.concrete.getter_name 👈() const {
    return m_👉f.name👈;
{%- else -%}
[[nodiscard]] inline const 👉 f.property_type 👈 👉 f.concrete.getter_name 👈() const {
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
Q_PROPERTY(const 👉 context.operation.root_type.name 👈 * data READ data NOTIFY dataChanged);

std::optional<👉 context.operation.root_type.name 👈 *> m_data = {};



inline const QString &ENV_NAME() override{
    static const auto ret = QString("👉 context.config.env_name 👈");
    return ret;
    }
signals:
    void dataChanged();

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
    if (!m_data){
        auto data = message.value("data").toObject();
        👉 context.operation.root_type.updater_name👈(👉 context.operation.root_type.concrete.name👈::instance(), data, this);
        m_data = new 👉 context.operation.root_type.name👈(this);
        emit dataChanged();
    }
    else{
    throw qtgql::exceptions::NotImplementedError({"Updates on root types is not implemented yet."});
    }
}

inline const 👉 context.operation.root_type.name 👈 * data() const{
    if (m_data){
        return m_data.value();
    }
    return nullptr;
}

{% if context.operation.variables %}
void set_variables(👉 context.operation.generated_variables_type 👈 vars){
vars_inst = vars;
m_variables = vars_inst.to_json();
}
{% endif %}

};
};

