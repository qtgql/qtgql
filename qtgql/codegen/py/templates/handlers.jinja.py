{% import "macros.jinja.py" as macros %}

from typing import Optional, Union
from PySide6.QtCore import Signal, QObject
from PySide6.QtQml import QmlElement, QmlSingleton
from qtgql.codegen.py.runtime.queryhandler import BaseQueryHandler, UseQueryABC, SelectionConfig
from qtgql.gqltransport.client import  GqlClientMessage, QueryPayload
from qtgql.codegen.py.runtime.bases import QGraphQListModel
from objecttypes import * # noqa


QML_IMPORT_NAME = "generated.{{context.config.env_name}}"
QML_IMPORT_MAJOR_VERSION = 1






{% for query in context.queries %}
@QmlElement
@QmlSingleton
class {{query.name}}(BaseQueryHandler[{{query.field.annotation}}]):
    ENV_NAME = "{{context.config.env_name}}"
    _message_template = GqlClientMessage(payload=QueryPayload(query="""{{query.query}}""", operationName="{{query.name}}"))

    OPERATION_CONFIG = {{query.operation_config}}

    def set_data(self, d: {{query.field.annotation}}) -> None:
        self._data = d
        self.dataChanged.emit()
    def update(self, data, config: SelectionConfig) -> None:
        parent = self
        {{ macros.update_field(query.field,  fset_name='self.dataChanged', private_name='self._data', include_selection_check=False) | indent(4, True) }}

    def deserialize(self, data: dict, config: SelectionConfig) -> None:
        parent = self
        {% set assign_to %}self._data{% endset %}
        {{ macros.deserialize_field(query.field,  assign_to, include_selection_check=False) | indent(4) }}
        self.dataChanged.emit()
    def on_data(self, message: dict) -> None:
        if not self._data:
            self.deserialize(message, self.OPERATION_CONFIG)

        # data existed and arrived data was null, empty data.
        elif not message.get('{{query.field.name}}', None):
            self._data = None
            self.dataChanged.emit()
        # data existed already, update the data
        else:
            self.update(message, self.OPERATION_CONFIG)

{% endfor %}


def init() -> None:
    {% for query in context.queries %}
    {{query.name}}()
    {% endfor %}
@QmlElement
class UseQuery(UseQueryABC):
    ENV_NAME = "{{context.config.env_name}}"