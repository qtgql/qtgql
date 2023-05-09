{% import "macros.jinja.hpp" as macros -%}
#include "./schema.hpp"

namespace 👉context.ns👈{



{% for t in context.operation.narrowed_types %}
class 👉 t.name 👈: public QObject{
    Q_OBJECT
👉context.schema_ns👈::👉 t.definition.name 👈* m_inst;

public:
    {% for f in t.fields %}
    {% endfor %}


};
{% endfor %}
};

