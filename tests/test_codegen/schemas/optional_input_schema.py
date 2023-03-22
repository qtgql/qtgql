from typing import Optional

import strawberry


@strawberry.type
class Query:
    @strawberry.field
    def echo_or_hello(self, echo: Optional[str] = None) -> str:
        return echo if echo else "Hello World!"


schema = strawberry.Schema(query=Query)

if __name__ == "__main__":
    ...
