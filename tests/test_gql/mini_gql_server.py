import asyncio
from typing import AsyncGenerator

from aiohttp import web
import strawberry
from strawberry.aiohttp.views import GraphQLView
from strawberry.types import Info


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "world"

    @strawberry.field
    def is_authenticated(self, info: Info) -> str:
        return info.context["request"].headers["Authorization"]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def pseudo_mutation(self) -> bool:
        return True


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def count(self, target: int = 10, raise_on_5: bool = False) -> AsyncGenerator[int, None]:
        for i in range(target):
            if raise_on_5 and i == 5:
                raise Exception("Test Gql Error")
            yield i
            await asyncio.sleep(0.001)


schema = strawberry.Schema(query=Query, subscription=Subscription, mutation=Mutation)


def init_func(argv):
    app = web.Application()
    app.router.add_route("*", "/graphql", GraphQLView(schema=schema))
    return app


if __name__ == "__main__":
    from aiohttp.web import main

    main(["mini_gql_server:init_func"])
