from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:  # pragma: no cover
    from qtgql.codegen.py.runtime.queryhandler import BaseQueryHandler
    from qtgql.gqltransport.client import HandlerProto


class NetworkLayerProto(Protocol):
    def execute(self, handler: HandlerProto) -> None:
        """accepts a handler and expected to call the handler's `on_data` /
        `on_error` / 'on_completed' when the operation is completed."""


class QtGqlEnvironment:
    """Encapsulates a schema interaction.

    The schema **must** be coherent with the schema use by the code
    generator. This class is used by the codegen and not to be
    instantiated directly.
    """

    def __init__(self, client: NetworkLayerProto, name: str):
        """
        :param client: The network layer for communicated the GraphQL server,
        all the generated handlers for this environment  would use this layer.
        :param name: This would be used to retrieve this environment from the env map by
        the generated handlers based on the configurations.
        """
        self.client = client
        self._query_handlers: dict[str, BaseQueryHandler] = {}
        self.name = name

    def add_query_handler(self, handler: BaseQueryHandler) -> None:
        self._query_handlers[handler.objectName()] = handler

    def get_handler(self, operation_name: str) -> BaseQueryHandler:
        return self._query_handlers[operation_name]


_ENV_MAP: dict[str, QtGqlEnvironment] = {}
"""In the future this would be usefully if you want to use different schemas,
maybe with a directive."""


def set_gql_env(env: QtGqlEnvironment) -> None:
    _ENV_MAP[env.name] = env


def get_gql_env(name: str) -> QtGqlEnvironment:
    return _ENV_MAP[name]
