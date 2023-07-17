from __future__ import annotations

import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def echo_or_hello(self, echo: str | None = None) -> str:
        return echo if echo else "Hello World!"


schema = strawberry.Schema(query=Query)

if __name__ == "__main__":
    ...
