from __future__ import annotations
from PySide6.QtCore import Property, Signal, QObject
from typing import Optional, Union
from qtgql.codegen.py.bases import get_base_graphql_object, BaseModel

BaseObject = get_base_graphql_object()

{% for type in types %}
class {{ type.name }}(BaseObject):
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

    @Property(type={{ f.property_type }}, fset={{ f.setter_name }}, notify={{f.signal_name}})
    def {{ f.name }}(self) -> {{ f.annotation }}:
        return self.{{  f.private_name  }}
    {% endfor %}
class {{ type.model_name }}(BaseModel):
    def __init__(self, data: list[{{  type.name  }}], parent: Optional[BaseObject] = None):
        super().__init__(data, parent)


{% endfor %}
