import asyncio
import random
from typing import AsyncGenerator, Optional

import strawberry
from aiohttp import web
from strawberry.aiohttp.views import GraphQLView
from strawberry.types import Info

from tests.conftest import fake


@strawberry.type
class Worm:
    name: str = strawberry.field(default_factory=fake.name)
    family: str = strawberry.field(
        default_factory=lambda: random.choice(
            ["Platyhelminthes", "Annelida", "Nemertea", "Nematoda", "Acanthocephala"]
        )
    )
    size: int = strawberry.field(default_factory=lambda: random.randint(10, 100))


@strawberry.type
class Apple:
    size: int = strawberry.field(default_factory=lambda: random.randint(10, 100))
    owner: str = strawberry.field(default_factory=fake.name)
    worms: Optional[list[Worm]] = strawberry.field()
    color: str = strawberry.field(default_factory=fake.color)


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "world"

    @strawberry.field
    def is_authenticated(self, info: Info) -> str:
        return info.context["request"].headers["Authorization"]

    @strawberry.field
    def apples(self) -> list[Apple]:
        return [Apple(worms=[Worm() for _ in range(5)] if fake.pybool() else []) for _ in range(30)]


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
