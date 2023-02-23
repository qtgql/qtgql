from typing import Optional, Union
from PySide6.QtCore import Signal, QObject
from PySide6.QtQml import QmlElement, QmlSingleton
from qtgql.codegen.py.runtime.queryhandler import BaseQueryHandler, UseQueryABC, SelectionConfig
from qtgql.gqltransport.client import  GqlClientMessage, QueryPayload
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
        # TODO: What about updates here?
        if {{query.field.name}} := message.get('{{query.field.name}}', None):
            self._data = {{query.field.type.type.name}}.from_dict(self, {{query.field.name}}, config)
        self.dataChanged.emit()

{% endfor %}


def init() -> None:
    {% for query in context.queries %}
    {{query.name}}()
    {% endfor %}
@QmlElement
class UseQuery(UseQueryABC):
    ENV_NAME = "{{context.config.env_name}}"