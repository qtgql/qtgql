{% import "macros.jinja.hpp" as macros -%}
#include "./schema.hpp"

namespace 👉context.ns👈{



{% for t in context.operation.narrowed_types %}
class 👉 t.name 👈: public QObject{
    Q_OBJECT
👉context.schema_ns👈::👉 t.definition.name 👈* m_inst;

public:
{% for f in t.fields %}

👉 f.type.annotation 👈  👉 f.definition.getter_name 👈() const {
    return m_inst->👉 f.definition.getter_name 👈();
};

{% endfor %}


};
{% endfor %}
};

