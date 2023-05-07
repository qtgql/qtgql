from qtgqlcodegen.tools import slot, qproperty



from typing import Optional, Union
from PySide6.QtCore import Signal, QObject
from PySide6.QtQml import QmlElement
from qtgqlcodegen.py.runtime.queryhandler import (BaseQueryHandler,
                                                   QmlOperationConsumerABC,
                                                   SelectionConfig,
                                                   OperationMetaData,
                                                   BaseMutationHandler,
                                                   BaseSubscriptionHandler)
from qtgqlcodegen.gqltransport.client import  GqlClientMessage, QueryPayload
from qtgqlcodegen.py.runtime.bases import QGraphQListModel
from .objecttypes import * # noqa


QML_IMPORT_NAME = "generated.yjMFhVofLsLMtRpHTKCC"
QML_IMPORT_MAJOR_VERSION = 1











class MainQuery(BaseQueryHandler[Optional[User]]):


    ENV_NAME = "yjMFhVofLsLMtRpHTKCC"
    OPERATION_METADATA = OperationMetaData(
        operation_name="MainQuery",
        selections=SelectionConfig(
    selections={

        "id":  None ,
        "name":  None ,
        "age":  None ,
        "agePoint":  None ,
        "male":  None ,
        "uuid":  None ,
    },

)

    )
    _message_template = GqlClientMessage(payload=QueryPayload(query="""query MainQuery {
  user {
  id name age agePoint male id uuid
  }
}
""
    ", operationName=" MainQuery "))

    def set_data(self, d
                 : Optional[User])
        ->None : self._data = d self.dataChanged
                                  .emit()

                                      def update(self, data
                                                 : dict)
                                  ->None
    : parent = self metadata = self.OPERATION_METADATA config =
    self.OPERATION_METADATA.selections

    field_data = data.get('user', None)

                     inner_config = config

                                    if not field_data : self.set_data(None) else
    :

    if self._data and self._data._id == field_data.get('id', None)
    : self._data
          .update(field_data, inner_config, metadata) else :

    self.set_data(User.from_dict(parent, field_data, inner_config, metadata))

        def loose(self)
          ->None : metadata = self.OPERATION_METADATA

                                    if self._data
    : self._data.loose(metadata) self._data = None

                                              def deserialize(self, data
                                                              : dict)
                                                  ->None
    : metadata = self.OPERATION_METADATA config = self.OPERATION_METADATA
                                                      .selections parent = self

    field_data = data.get('user', None)

                     inner_config = config

                                    if field_data : self._data =
        User.from_dict(parent, field_data, inner_config, metadata, )

            self.dataChanged.emit() def on_data(self, message
                                                : dict)
                ->None : if not self._data
    : self.deserialize(message)

#data existed and arrived data was null, empty data.
          elif not message.get('user', None)
    : self._data = None self.dataChanged
                       .emit()
#data existed already, update the data
                           else
    : self.update(message)

          @QmlElement class ConsumeMainQuery(QmlOperationConsumerABC)
    :

      dataChanged =
            Signal()

                @qproperty(type = QObject, notify = dataChanged) def
            handlerData(self)
                ->Optional[User] : return self._handler
                ._data

                                   def _get_handler(self)
                ->BaseQueryHandler[Optional[User]] : return MainQuery(self)
