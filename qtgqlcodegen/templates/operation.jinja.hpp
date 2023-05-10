{% import "macros.jinja.hpp" as macros -%}
#include "./schema.hpp"

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
};

