from __future__ import annotations

import strawberry


@strawberry.input()
class What:
    what: list[str]


@strawberry.type
class Query:
    @strawberry.field
    def echo(self, what: What) -> list[str]:
        return what.what


schema = strawberry.Schema(query=Query)
