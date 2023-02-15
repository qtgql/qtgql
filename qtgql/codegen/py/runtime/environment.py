from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from qtgql.gqltransport.client import GqlWsTransportClient, HandlerProto

if TYPE_CHECKING:  # pragma: no cover
    from qtgql.codegen.py.runtime.queryhandler import BaseQueryHandler


class NetworkProto(Protocol):
    def execute(self, handler: HandlerProto) -> None:
        """accepts a handler and expected to call the handler's `on_data` /
        `on_error` / 'on_completed' when the operation is completed."""


class QtGqlEnvironment:
    """Encapsulates a schema interaction.

    The schema **must** be coherent with the schema use by the code
    generator. This class is used by the codegen and not to be
    instantiated directly.
    """

    def __init__(self, client: NetworkProto):
        self.client = client
        self.query_handlers: dict[int, BaseQueryHandler] = {}

    @classmethod
    def from_url(cls, url: str):
        return cls(client=GqlWsTransportClient(url=url))


ENV_MAP: dict[str, QtGqlEnvironment] = {}
"""In the future this would be usefully if you want to use different schemas,
maybe with a directive."""


def get_default_env() -> QtGqlEnvironment:
    return ENV_MAP["DEFAULT"]
