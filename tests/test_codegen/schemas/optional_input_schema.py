from __future__ import annotations

import mimesis
import strawberry

from tests.conftest import factory


@strawberry.type
class Query:
    @strawberry.field
    def echo_or_hello(self, echo: str | None = None) -> str:
        ret = echo if echo else "Hello World!"
        ret += factory.text.text()
        return ret


schema = strawberry.Schema(query=Query)
