from __future__ import annotations
from PySide6.QtCore import Property, Signal, QObject
from typing import Optional

{% for type in types %}
class {{ type.name }}(QObject):
    """{{  type.docstring  }}"""
    def __init__(self, parent: QObject = None, {% for p in type.properties %} {{p.name}}: Optional[{{p.type}}] = {{p.default}} {% endfor %}):
        super().__init__(parent)
        {% for p in type.properties %}
        self.{{  p.private_name  }} = {{p.name}}
        {% endfor %}


    {% for p in type.properties %}
    {{ p.signal_name }} = Signal()

    def {{ p.setter_name }}(self, v: {{  p.type  }}) -> None:
        self.{{  p.private_name  }} = v
        self.{{  p.name  }}Changed.emit()

    @Property(type={{ p.type }}, fset={{ p.setter_name }}, notify={{p.signal_name}})
    def {{ p.name }}(self) -> {{ p.type }}:
        return self.{{  p.private_name  }}
    {% endfor %}

{% endfor %}
