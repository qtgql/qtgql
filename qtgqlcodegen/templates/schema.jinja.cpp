#include "schema.hpp"

namespace 👉 context.config.env_name 👈{
{% for interface in context.interfaces -%}
std::shared_ptr<👉 interface.name 👈> 👉 interface.name 👈::from_json(const QJsonObject& data,
                                                     const qtgql::bases::SelectionsConfig &config,
                                                     const qtgql::bases::OperationMetadata& metadata){
    auto tp_name = data["__typename"].toString();
    {% for impl in interface.implementations.values() -%}
    if ("👉 impl.name 👈" == tp_name){
        return std::static_pointer_cast<👉 interface.name 👈>(👉 impl.name 👈::from_json(data, config, metadata));
    }
    {% endfor %}
    }
{% endfor %}
}