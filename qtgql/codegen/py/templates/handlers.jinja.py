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

    def on_data(self, message: dict) -> None:
        config = self.OPERATION_CONFIG
        # TODO: this should be a copy of the `from_dict()` template.
        field_data = message.get('{{query.field.name}}', None)
        {% if query.field.type.is_object_type %}
        if not field_data:
            emit = False
            if self._data:
                emit = True
            self._data = None
            if emit:
                self.dataChanged.emit()
        else:
            if self._data and self._data._id == field_data['id']:
                self._data.update(field_data, config)
            else:
                self._data = {{query.field.type.is_object_type.name}}.from_dict(
                    self,
                    field_data,
                    config
                )
                self.dataChanged.emit()
        {% elif query.field.type.is_model %}
        if field_data:
            if self._data:
                self._data.update(field_data, config)
            else:
                self._data = QGraphQListModel(
                    parent=self,
                    data=[{{ query.field.type.is_model.name }}.from_dict(self, data=node, config=config) for node in field_data],
                    default_type={{ query.field.type.is_model.name }},
                )
                self.dataChanged.emit()
        {% endif %}

{% endfor %}


def init() -> None:
    {% for query in context.queries %}
    {{query.name}}()
    {% endfor %}
@QmlElement
class UseQuery(UseQueryABC):
    ENV_NAME = "{{context.config.env_name}}"