from __future__ import annotations

import asyncio
import random
from typing import AsyncGenerator
from typing import Optional
from typing import TYPE_CHECKING

import strawberry
from aiohttp import web
from faker import Faker
from strawberry.aiohttp.handlers import GraphQLTransportWSHandler
from strawberry.aiohttp.views import GraphQLView

from tests.conftest import hash_schema
from tests.test_codegen.schemas import __all__ as all_schemas
from tests.test_codegen.schemas.node_interface import Node

if TYPE_CHECKING:
    from strawberry.types import Info

fake = Faker()


@strawberry.type
class Worm(Node):
    name: str = strawberry.field(default_factory=fake.name)
    family: str = strawberry.field(
        default_factory=lambda: random.choice(  # noqa: S311
            ["Platyhelminthes", "Annelida", "Nemertea", "Nematoda", "Acanthocephala"],
        ),
    )
    size: int = strawberry.field(default_factory=lambda: random.randint(10, 100))  # noqa: S311


@strawberry.type
class Apple(Node):
    size: int = strawberry.field(default_factory=lambda: random.randint(10, 100))  # noqa: S311
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


class DebugGraphQLTransportWSHandler(GraphQLTransportWSHandler):
    async def handle_message(self, message: dict):
        print(f"message -> {message}")  # noqa
        await super().handle_message(message)


class DebugGqlView(GraphQLView):
    graphql_transport_ws_handler_class = DebugGraphQLTransportWSHandler


app = web.Application()
app.router.add_route("*", "/graphql", DebugGqlView(schema=schema))
for mod in all_schemas:
    app.router.add_route("*", f"/{hash_schema(mod.schema)}", DebugGqlView(schema=mod.schema))


def init_func(argv):
    return app


def main(port: int = 9000):
    web.run_app(app, host="localhost", port=port)


if __name__ == "__main__":
    main()
