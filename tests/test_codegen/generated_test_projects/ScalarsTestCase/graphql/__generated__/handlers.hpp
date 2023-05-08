from qtgqlcodegen.tools import slot,
    qproperty

        from typing import Optional,
    Union from PySide6.QtCore import Signal,
    QObject from PySide6.QtQml import QmlElement from qtgqlcodegen.py.runtime
        .queryhandler
        import(BaseQueryHandler, QmlOperationConsumerABC, SelectionConfig,
               OperationMetaData, BaseMutationHandler, BaseSubscriptionHandler)
            from qtgqlcodegen.gqltransport.client import GqlClientMessage,
    QueryPayload from qtgqlcodegen.py.runtime.bases import
    QGraphQListModel from.objecttypes import *#noqa

    QML_IMPORT_NAME =
        "generated.{{context.config.env_name}}" QML_IMPORT_MAJOR_VERSION = 1

    class {
  { query.name }
}(BaseQueryHandler[{{query.field.annotation}}])
    :

      {{operation_classvars(query)}} {
  { operation_common(query) }
}

@QmlElement class Consume {
  { query.name }
}(QmlOperationConsumerABC) : {
  { operation_consumer_common(query) }
}
def _get_handler(self)->BaseQueryHandler[{{query.field.annotation}}]
    : return {{query.name}}(self)
