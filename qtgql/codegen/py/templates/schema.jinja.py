from __future__ import annotations
from PySide6.QtCore import Property, Signal, QObject, QEnum
from PySide6.QtQml import QmlElement, QmlSingleton
from enum import Enum, auto
from typing import Optional, Union
from qtgql.tools import qproperty
from qtgql.codegen.py.runtime.bases import QGraphQListModel
from qtgql.gqltransport.client import  GqlClientMessage, QueryPayload
from qtgql.codegen.py.runtime.queryhandler import BaseQueryHandler
from qtgql.codegen.py.compiler.config import QtGqlConfig




{% for dep in context.dependencies %}
{{dep}}{% endfor %}


QML_IMPORT_NAME = "{{context.config.qml_import_name}}"
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

    DEFAULT_INIT_DICT = dict({% for f in type.fields %}
        {{f.name}}=None,{% endfor %}
    )
    def __init__(self, parent: QObject = None, {% for f in type.fields %} {{f.name}}: {{f.annotation}} = None, {% endfor %}):
        super().__init__(parent){% for f in type.fields %}
        self.{{  f.private_name  }} = {{f.name}} if {{f.name}} else {{f.default_value}}{% endfor %}

    @classmethod
    def from_dict(cls, parent,  data: dict) -> {{type.name}}:
        init_dict = cls.DEFAULT_INIT_DICT.copy()
        {% for f in type.fields %}
        if {{f.name}} := data.get('{{f.name}}', None):
            init_dict['{{f.name}}'] = {{f.deserializer}}{% endfor %}
        return cls(
            parent=parent,
            **init_dict
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

{% endfor %}


{% for query in context.queries %}
@QmlElement
class {{query.name}}(BaseQueryHandler[{{query.field.annotation}}]):
    ENV_NAME = "{{context.config.env_name}}"
    _message_template = GqlClientMessage(payload=QueryPayload(query="", operationName="{{query.name}}"))
    def on_data(self, message: dict) -> None:
        parent = self.parent()
        if {{query.field.name}} := message.get('{{query.field.name}}', None):
            self._data = {{query.field.deserializer}}
            self.dataChanged.emit()

{% endfor %}