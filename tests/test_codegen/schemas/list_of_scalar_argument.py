from __future__ import annotations

import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def echo(self, what: list[str]) -> list[str]:
        return what


schema = strawberry.Schema(query=Query)
