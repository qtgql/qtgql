{ % import "macros.jinja.cpp" as macros % }
#include <QObject>
#include <graphqlmetadata.hpp>

{ % macro init_and_props(type) % }

public:
{{type.name}}(QObject* parent = None, { % for f in type.fields % } {{f.name}}
              : Optional[{{f.annotation}}] = None, { % endfor % })
    : QObject::QObject(parent) {
  {% for f in type.fields %}
  {{f.private_name}} = { {f.name} } if {
    { f.name }
  }
  else {{f.default_value}} {
    % endfor %
  }
};

{%for f in type.fields %}
void{{f.setter_name}}(const {{f.annotation}} &
                      v){{{f.private_name}} = v emit{{f.signal_name}}()};
{% endfor %}

signals:
{%for f in type.fields %}
void{{f.signal_name}}();
{% endfor %}

{% endmacro %}  // ----------------------------------------- Object Types
                  // -----------------------------------------
{% for type in context.types %}
class {{ type.name }} : public {% if type.has_id_field %}
_BaseQGraphQLObjectWithID{ % else % } _BaseQGraphQLObject{ % endif % }, {% for base in type.implements %}
{{base.name}}, { % endfor % } {

                   static const QString TYPE_NAME = "{{type.name}}"

                   {{init_and_props(type)}}

                   std::shared_ptr<{{type.name}}>
                       from_json(QObject * parent, const QJsonObject& data,
                                 const SelectionConfig& config,
                                 const OperationMetaData& metadata){
                           auto inst = std::make_shared<{{type.name}}>();
{% for f in type.fields -%
}
{ % set assign_to % } inst.{{f.private_name}} { % endset % } {
    {macros.deserialize_field(f, assign_to) | indent(8)}} { % -endfor % } {
  % if type.id_is_optional %
}
if (inst->id) {
  auto record = NodeRecord(node = inst, retainers = set())
                    .retain(metadata.operation_name)
                        cls.__store__.add_record(record)
}
{ % elif type.has_id_field and not type.id_is_optional % } record =
    NodeRecord(node = inst, retainers = set())
        .retain(metadata.operation_name) cls.__store__.add_record(record) {
  % endif %
}
return inst
}
}
;
{ % endfor % }
