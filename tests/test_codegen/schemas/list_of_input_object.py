from __future__ import annotations

import strawberry


@strawberry.input()
class Echo:
    value: str


@strawberry.input()
class What:
    echo: list[Echo] | None


@strawberry.type
class Query:
    @strawberry.field
    def echo(self, what: What | None = None) -> list[str]:
        return [o.value for o in what.echo]


schema = strawberry.Schema(query=Query)
