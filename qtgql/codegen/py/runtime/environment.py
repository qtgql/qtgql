from __future__ import annotations

from typing import TYPE_CHECKING

from qtgql.gqltransport.client import GqlWsTransportClient

if TYPE_CHECKING:
    from qtgql.codegen.py.runtime.queryhandler import BaseQueryHandler


class QtGqlEnvironment:
    """Encapsulates a schema interaction.

    The schema **must** be coherent with the schema use by the code
    generator. This class is used by the codegen and not to be
    instantiated directly.
    """

    def __init__(self, client: GqlWsTransportClient):
        self.client = client
        self.query_handlers: dict[int, BaseQueryHandler] = {}

    def register_query(self, handler: BaseQueryHandler):
        self.query_handlers[hash(handler)] = handler

    @classmethod
    def from_url(cls, url: str):
        return cls(client=GqlWsTransportClient(url=url))

    def get_handler_by_query(self, query_id: int) -> BaseQueryHandler:
        return self.query_handlers[query_id]

    def fetch_all(self):
        """Fetches all registered query handlers."""
        for query in self.query_handlers.values():
            query.fetch()


ENV_MAP: dict[str, QtGqlEnvironment] = {}
"""In the future this would be usefully if you want to use different schemas,
maybe with a directive."""


def get_default_env() -> QtGqlEnvironment:
    return ENV_MAP["DEFAULT"]
