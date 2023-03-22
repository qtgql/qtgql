{% import "macros.jinja.py" as macros %}
from __future__ import annotations
from PySide6.QtCore import Signal, QObject, QEnum

from PySide6.QtQuick import QQuickItem
from typing import Optional, Union
from enum import Enum, auto
from PySide6.QtQml import QmlElement, QmlSingleton

from qtgql.codegen.py.runtime.queryhandler import SelectionConfig, OperationMetaData
from qtgql.tools import qproperty
from qtgql.codegen.py.runtime.bases import QGraphQListModel, NodeRecord, QGraphQLInputObjectABC

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
    
    def loose(self, metadata: OperationMetaData) -> None:
        metadata=metadata  {# no-op for types without children #}
        {# loose children #}
        {% for f in type.fields -%}
        {% set private_name %}self.{{f.private_name}}{% endset %}
        {{ macros.loose_field(f, private_name) }}
        {% endfor %}
        {# loose self #}
        {% if type.id_is_optional %}
        if self._id:
            self.__store__.loose(self, metadata.operation_name)
        {% elif type.has_id_field and not type.id_is_optional %}
        self.__store__.loose(self, metadata.operation_name)
        {% else %} {# type with no ID wouldn't clear up itself at the store. delete it here. #}
        self.deleteLater()
        {% endif %}


    @classmethod
    def from_dict(cls, parent, data: dict, config: SelectionConfig, metadata: OperationMetaData) -> {{type.name}}:
        {% if type.id_is_optional %}
        if id_ := data.get('id', None):
            if instance := cls.__store__.get_node(id_):
                instance.update(data, config, metadata)
                return instance
        {% elif type.has_id_field %}
        if instance := cls.__store__.get_node(data['id']):
            instance.update(data, config, metadata)
            return instance
        {% endif %}
        inst = cls(parent=parent)
        {% for f in type.fields -%}
        {% set assign_to %}inst.{{f.private_name}}{% endset %}
        {{ macros.deserialize_field(f,  assign_to) | indent(8)}}
        {%- endfor %}
        {% if type.id_is_optional %}
        if inst.id:
            record = NodeRecord(node=inst, retainers=set()).retain(metadata.operation_name)
            cls.__store__.add_record(record)
        {% elif type.has_id_field and not type.id_is_optional %}
        record = NodeRecord(node=inst, retainers=set()).retain(metadata.operation_name)
        cls.__store__.add_record(record)
        {% endif %}
        return inst

    def update(self, data, config: SelectionConfig, metadata: OperationMetaData) -> None:
        parent = self.parent()
        {%for f in type.fields %}{% set fset %}self.{{f.setter_name}}{% endset %}{% set private_name %}self.{{f.private_name}}{% endset %}
        {{ macros.update_field(f, fset_name=fset, private_name=private_name) | indent(8, True) }}{% endfor %}

__TYPE_MAP__['{{ type.name }}'] = {{ type.name }}
{% endfor %}

{# --------- INPUT OBJECTS ---------- #}

{% for type in context.input_objects %}
class {{type.name}}(QGraphQLInputObjectABC):
    """{{  type.docstring  }}"""


    def __init__(self, parent: QObject = None, {% for f in type.fields %} {{f.name}}: {{f.annotation}} = None, {% endfor %}):
        super().__init__(parent){% for f in type.fields %}
        self.{{f.name}} = {{f.name}}{% endfor %}


    def asdict(self) -> dict:
        ret = {}
        {% for f in type.fields %}{% set attr_name %}self.{{f.name}}{% endset %}
        if {{attr_name}}:
            ret['{{f.name}}'] = {{f.json_repr(attr_name)}}
        {% endfor %}
        return ret


{% endfor %}