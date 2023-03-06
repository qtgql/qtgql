{% import "macros.jinja.py" as macros %}
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

__TYPE_MAP__: dict[str, type[{{context.base_object_name}}]] = {}


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
    {%for f in type.fields %}
    {{f.signal_name}} = Signal()

    def {{f.setter_name}}(self, v: {{f.annotation}}) -> None:
        self.{{f.private_name}} = v
        self.{{f.signal_name}}.emit()

    @qproperty(type={{f.property_type}}, fset={{f.setter_name}}, notify={{f.signal_name}})
    def {{f.name}}(self) -> {{f.fget_annotation}}:
        {{f.fget}}
    {% endfor %}
    

    @classmethod
    def from_dict(cls, parent, data: dict, config: SelectionConfig) -> {{type.name}}:
        {% if type.id_is_optional %}
        if id_ := data.get('id', None):
            if instance := cls.__store__.get_node(id_):
                instance.update(data, config)
                return instance
        {% elif type.has_is_field %}
        if instance := cls.__store__.get_node(data['id']):
            instance.update(data, config)
            return instance
        {% endif %}
        {% if type.has_is_field%}
        else:
        {% endif %}
            inst = cls(parent=parent)
            {% for f in type.fields -%}
            {% set assign_to %}inst.{{f.private_name}}{% endset %}
            {{ macros.deserialize_field(f,  assign_to) | indent(12)}}
            {%- endfor %}
            {% if type.id_is_optional %}
            if inst.id:
                cls.__store__.set_node(inst)
            {% elif type.has_id_field and not type.id_is_optional %}
            cls.__store__.set_node(inst)
            {% endif %}
            return inst
    def update(self, data, config: SelectionConfig) -> None:
        parent = self.parent()
        {%for f in type.fields %}{% set fset %}self.{{f.setter_name}}{% endset %}{% set private_name %}self.{{f.private_name}}{% endset %}
        {{ macros.update_field(f, fset_name=fset, private_name=private_name) | indent(8, True) }}{% endfor %}

__TYPE_MAP__['{{ type.name }}'] = {{ type.name }}
{% endfor %}


