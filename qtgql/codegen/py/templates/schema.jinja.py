from __future__ import annotations
from PySide6.QtCore import Property, Signal, QObject, QEnum
from PySide6.QtQml import QmlElement
from enum import Enum, auto
from typing import Optional, Union
from qtgql import qproperty
from qtgql.codegen.py.bases import BaseModel
from qtgql.codegen.py.config import QtGqlConfig


{% for dep in context.dependencies %}
{{dep}}{% endfor %}


QML_IMPORT_NAME = "QtGql"
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

    def __init__(self, parent: QObject = None, {% for f in type.fields %} {{f.name}}: {{f.annotation}} = None, {% endfor %}):
        super().__init__(parent){% for f in type.fields %}
        self.{{  f.private_name  }} = {{f.name}}{% endfor %}

    @classmethod
    def from_dict(cls, parent,  data: dict) -> {{type.name}}:
        return cls(
        parent=parent,{% for f in type.fields %}
        {{f.name}} = {{f.deserializer}},{% endfor %}
        )

    {% for f in type.fields %}
    {{ f.signal_name }} = Signal()

    def {{ f.setter_name }}(self, v: {{  f.annotation  }}) -> None:
        self.{{  f.private_name  }} = v
        self.{{  f.name  }}Changed.emit()

    @qproperty(type={{f.property_type}}, fset={{ f.setter_name }}, notify={{f.signal_name}})
    def {{ f.name }}(self) -> {{ f.fget_annotation }}:
        {{f.fget}}
    {% endfor %}
class {{ type.model_name }}(BaseModel):
    def __init__(self, data: list[{{  type.name  }}], parent: Optional[{{context.base_object_name}}] = None):
        super().__init__(data, parent)


{% endfor %}
