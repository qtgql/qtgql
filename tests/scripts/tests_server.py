from __future__ import annotations

import random
from typing import TYPE_CHECKING, AsyncGenerator

import strawberry
from aiohttp import web
from faker import Faker
from strawberry.aiohttp.handlers import GraphQLTransportWSHandler
from strawberry.aiohttp.views import AioHTTPRequestAdapter, GraphQLView

from tests.test_codegen.schemas.node_interface import Node
from tests.test_codegen.testcases import implemented_testcases

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
    worms: list[Worm] | None = strawberry.field()
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

    @strawberry.field()
    def raiseError(self) -> None:
        raise Exception("foobar")


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


schema = strawberry.Schema(query=Query, subscription=Subscription, mutation=Mutation)


class DebugGraphQLTransportWSHandler(GraphQLTransportWSHandler):
    async def handle_message(self, message: dict):
        print(f"TestCase{self.testcase_name}: WS[{self._ws._req.path}] message -> {message}")  # noqa
        await super().handle_message(message)


class DebugHttpHandler(AioHTTPRequestAdapter):
    async def get_body(self) -> str:
        ret = await super().get_body()
        print(f"[{self.request.rel_url}-{self.testcase_name}] message -> {ret}")  # noqa
        return ret


class DebugGqlView(GraphQLView):
    graphql_transport_ws_handler_class = DebugGraphQLTransportWSHandler
    request_adapter_class = DebugHttpHandler

    def __init__(self, testcase_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.graphql_transport_ws_handler_class.testcase_name = testcase_name
        self.request_adapter_class.testcase_name = testcase_name


app = web.Application()
app.router.add_route("*", "/graphql", DebugGqlView("main test schema", schema=schema))


for tst_case in implemented_testcases:
    app.router.add_route(
        "*",
        f"/{tst_case.test_name}",
        DebugGqlView(tst_case.test_name, schema=tst_case.schema),
    )


def init_func(argv):
    return app


def main(port: int = 9000):
    web.run_app(app, host="localhost", port=port)


if __name__ == "__main__":
    main()
