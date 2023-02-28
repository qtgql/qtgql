from __future__ import annotations
from PySide6.QtCore import Signal, QObject, QEnum

from PySide6.QtQuick import QQuickItem
from typing import Optional, Union
from enum import Enum, auto
from PySide6.QtQml import QmlElement, QmlSingleton

from qtgql.codegen.py.runtime.queryhandler import SelectionConfig
from qtgql.tools import qproperty
from qtgql.codegen.py.runtime.bases import QGraphQListModel






{% for dep in context.dependencies %}
{{dep}}{% endfor %}


QML_IMPORT_NAME = "generated.{{context.config.env_name}}.types"
QML_IMPORT_MAJOR_VERSION = 1



{% for enum in context.enums %}
class {{enum.name}}(Enum):
    {% for member in enum.members %}
    {{member.name}} = auto()
    """{{member.description}}"""{% endfor %}

{% endfor %}

{% if context.enums %}
@QmlElement
class Enums(QObject):
    {% for enum in context.enums %}
    QEnum({{enum.name}})
    {% endfor %}
{% endif %}


class SCALARS:
    {% for scalar in context.custom_scalars %}
    {{scalar}} = {{scalar}}{% endfor %}

{% for type in context.types %}
class {{ type.name }}({{context.base_object_name}}):
    """{{  type.docstring  }}"""


    def __init__(self, parent: QObject = None, {% for f in type.fields %} {{f.name}}: Optional[{{f.annotation}}] = None, {% endfor %}):
        super().__init__(parent){% for f in type.fields %}
        self.{{  f.private_name  }} = {{f.name}} if {{f.name}} else {{f.default_value}}{% endfor %}

    def update(self, data, config: SelectionConfig) -> None:
        parent = self.parent()
        {%for f in type.fields %}
        if '{{f.name}}' in config.selections.keys():
            field_data = data.get('{{f.name}}', {{f.default_value}})
            {% if f.type.is_object_type %}
            if not field_data:
                self.{{f.setter_name}}(None)
            else:
                self.{{f.setter_name}}({{f.type.is_object_type.name}}.from_dict(
                    parent,
                    field_data,
                    config.selections['{{f.name}}']
                ))
            {% elif f.type.is_model %}
            self.{{f.setter_name}}(QGraphQListModel(parent,
                                                  data=[
                                                      {{f.type.is_model.name}}.from_dict(parent, data,
                                                                                         config.selections[{{f.name}}])
                                                      for data in {{f.name}}
                                                  ],
                                                  default_object={{f.type.is_model}}.default_instance()
                                                  ))
            {% elif f.type.is_builtin_scalar %}
            if self.{{f.private_name}} != field_data:
                self.{{f.setter_name}}(field_data)
            {% elif f.is_custom_scalar %}
            new = SCALARS.{{f.is_custom_scalar.__name__}}.from_graphql(field_data)
            if new != self.{{f.private_name}}:
                self.{{f.setter_name}}(new)
            {% elif f.type.is_enum %}
            self.{{f.setter_name}}({{f.type.is_enum.name}}[field_data])
            {% elif f.type.is_union() %}
            type_name = field_data['__typename']
            choice = config.selections['{{f.name}}'].choices[type_name]
            self.{{f.setter_name}}(cls.type_map[type_name].from_dict(parent, field_data, choice))
            {% endif %}
            {% endfor %}

    @classmethod
    def from_dict(cls, parent, data: dict, config: SelectionConfig) -> {{type.name}}:
        if instance := cls.__store__.get_node(data['id']):
            instance.update(data, config)
            return instance
        else:
            inst = cls(parent=parent)
            {% for f in type.fields %}
            if '{{f.name}}' in config.selections.keys():
                field_data = data.get('{{f.name}}', {{f.default_value}})
                {% if f.type.is_object_type %}
                if field_data:
                    inst.{{f.private_name}} = {{f.type.is_object_type.name}}.from_dict(
                        parent,
                        field_data,
                        config.selections['{{f.name}}']
                    )
                {% elif f.type.is_model %}
                inst.{{f.private_name}} = QGraphQListModel(parent,
                                                      data=[
                                                          {{f.type.is_model.name}}.from_dict(parent, data,
                                                                                             config.selections[
                                                                                                 {{f.name}}])
                                                          for data in {{f.name}}
                                                      ],
                                                      default_object={{f.type.is_model}}.default_instance()
                                                      )
                {% elif f.type.is_builtin_scalar %}
                inst.{{f.private_name}} = field_data
                {% elif f.is_custom_scalar %}
                inst.{{f.private_name}} = SCALARS.{{f.is_custom_scalar.__name__}}.from_graphql(field_data)
                {% elif f.type.is_enum %}
                inst.{{f.private_name}} = {{f.type.is_enum.name}}[field_data]
                {% elif f.type.is_union() %}
                type_name = field_data['__typename']
                choice = config.selections['{{f.name}}'].choices[type_name]
                inst.{{f.private_name}} = cls.type_map[type_name].from_dict(parent, field_data, choice)
                {% endif %}
                {% endfor %}
            cls.__store__.set_node(inst)
            return inst

    {% for f in type.fields %}
    {{ f.signal_name }} = Signal()

    def {{ f.setter_name }}(self, v: {{  f.annotation  }}) -> None:
        self.{{  f.private_name  }} = v
        self.{{  f.signal_name  }}.emit()

    @qproperty(type={{f.property_type}}, fset={{ f.setter_name }}, notify={{f.signal_name}})
    def {{ f.name }}(self) -> {{ f.fget_annotation }}:
        {{f.fget}}
    {% endfor %}

{% endfor %}



