{% import "macros.jinja.hpp" as macros -%}
#include "./schema.hpp"

namespace 👉context.operation.name👈{



{% for t in context.operation.narrowed_types %}
class t.name: public QObject{
    Q_OBJECT


};
{% endfor %}
};

