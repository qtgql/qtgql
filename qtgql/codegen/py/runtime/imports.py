from typing import ClassVar, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtQuick import QQuickItem

from qtgql.codegen.py.runtime.environment import get_gql_env
from qtgql.tools import qproperty, slot


class UseQueryABC(QQuickItem):
    """Concrete implementation in the template."""

    graphqlChanged = Signal()
    ENV_NAME: ClassVar[str]

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._graphql: Optional[str] = None
        self.env = get_gql_env(self.ENV_NAME)
        self.env._query_handlers

    @slot
    def set_graphql(self, graphql: str) -> None:
        self._graphql = graphql
        self.graphqlChanged.emit()  # type: ignore

    @qproperty
    def graphql(self):
        return self._graphql
