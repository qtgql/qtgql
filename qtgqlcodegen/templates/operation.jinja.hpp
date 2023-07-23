{%- from "macros/deserialize_concrete_field.jinja.hpp" import  deserialize_concrete_field -%}
{%- from "macros/proxy_type_fields.jinja.hpp" import  proxy_type_fields -%}
{%- from "macros/update_proxy_field.jinja.cpp" import  update_proxy_field -%}
#pragma once
#include "./schema.hpp"
#include <qtgql/gqlwstransport/gqlwstransport.hpp>
#include <QObject>
#include <QtQml/qqmlregistration.h>

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

// ------------ Narrowed Interfaces ------------
{% for t in context.operation.interfaces -%}
class 👉 t.name 👈: public 👉 context.qtgql_types.ObjectTypeABC.name 👈{

👉 proxy_type_fields(t, context) 👈
public:
    using 👉 context.qtgql_types.ObjectTypeABC.name 👈::👉 context.qtgql_types.ObjectTypeABC.last 👈;
{% for f in t.fields -%}
[[nodiscard]] inline virtual const 👉 f.type.property_type 👈  👉 f.concrete.getter_name 👈() const {
throw qtgql::exceptions::InterfaceDirectAccessError("👉t.concrete.name👈");
}
{% endfor %}
};
{% endfor %}
// ------------ Narrowed Object types ------------
{% for t in context.operation.narrowed_types %}
class 👉 t.name 👈: public 👉 context.qtgql_types.ObjectTypeABC.name if not t.base_interface else t.base_interface.name 👈{

👉context.operation.name👈* m_operation;

👉 proxy_type_fields(t, context) 👈
public:
{% if t.concrete.is_root -%}
👉 t.name 👈(👉 context.operation.name 👈 * operation);
{% else -%}
👉 t.name 👈(👉 context.operation.name 👈 * operation, const std::shared_ptr<👉 t.concrete.name 👈> &inst);
{% endif %}
{% if  not t.concrete.is_root -%}
void qtgql_replace_concrete(const std::shared_ptr<👉 t.concrete.name 👈> & new_inst);
{% endif %}
protected:
    void _qtgql_connect_signals();
public:
{% for f in t.fields -%}
[[nodiscard]] const 👉 f.type.property_type 👈  👉 f.concrete.getter_name 👈() const;
{% endfor -%}
public:
[[nodiscard]] const QString & __typename() const final{
    return m_inst->__typename();
}
};
{% endfor %}

struct 👉 context.operation.generated_variables_type 👈{
{% for var in context.operation.variables -%}
std::optional<👉 var.type.member_type 👈> 👉 var.name 👈 = {};
{% endfor -%}
    QJsonObject to_json() const{
    QJsonObject __ret;
    {% for var in context.operation.variables -%}
    if (👉 var.name 👈.has_value()){
    __ret.insert("👉 var.name 👈",  👉 var.json_repr() 👈);
    }
    {% endfor -%}
    return __ret;
    }
};

class 👉 context.operation.name 👈: public qtgql::gqlwstransport::OperationHandlerABC{
    Q_OBJECT
    Q_PROPERTY(const 👉 context.operation.root_type.name 👈 * data READ data NOTIFY dataChanged);
    QML_ELEMENT
    QML_UNCREATABLE("Must be instantiated as with shared.")

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
    auto data = message.value("data").toObject();
    if (!m_data){
        👉 context.operation.root_type.updater_name👈(👉 context.operation.root_type.concrete.name👈::instance(), data, this);
        m_data = new 👉 context.operation.root_type.name👈(this);
        emit dataChanged();
    }
    else{
        👉 context.operation.root_type.updater_name👈(👉 context.operation.root_type.concrete.name👈::instance(), data, this);
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

{# // This class exists as an alias class to an operation for qml, since operations
// must be created with shared pointers. -#}
class Use👉 context.operation.name 👈: public QObject{
    Q_OBJECT
    QML_ELEMENT
    Q_PROPERTY(const 👉 context.operation.root_type.name 👈 * data READ data NOTIFY dataChanged);
    Q_PROPERTY(bool completed READ completed NOTIFY completedChanged)
    Q_PROPERTY(bool operationOnFlight READ operation_on_flight NOTIFY operationOnFlightChanged)

public:
std::shared_ptr<👉 context.operation.name 👈> m_operation;

Use👉 context.operation.name 👈(QObject *parent = nullptr): QObject(parent){
    m_operation = 👉 context.operation.name 👈::shared();
    auto op_ptr = m_operation.get();
    connect(op_ptr, &👉 context.operation.name 👈::dataChanged, this, [&]{emit dataChanged();});
    connect(op_ptr, &👉 context.operation.name 👈::completedChanged, this, [&]{emit completedChanged();});
    connect(op_ptr, &👉 context.operation.name 👈::operationOnFlightChanged, this, [&]{emit operationOnFlightChanged();});
};

inline const 👉 context.operation.root_type.name 👈 * data() const{
    return m_operation->data();
}
inline bool completed() const{
    return m_operation->completed();
}
inline bool operation_on_flight() const{
    return m_operation->operation_on_flight();
}

public slots:
void fetch(){
    m_operation->fetch();
};
void refetch(){
    m_operation->refetch();
};

signals:
void dataChanged();
void completedChanged();
void operationOnFlightChanged();
};
};
