import strawberry
from strawberry.types import Info

from tests.test_codegen.schemas.node_interface import Node

countrymap = {"isr": "Israel", "uk": "United Kingdom"}


@strawberry.scalar(
    name="Country",
    description="countries by codename",
    serialize=lambda v: v,
    parse_value=lambda v: countrymap[v],
)
class Country:
    ...


@strawberry.type
class User(Node):
    name: str
    age: int
    country: Country

@strawberry.type
class Query:
    _prev = ""

    @strawberry.field()
    def user(self, info: Info) -> User:
        return User(name="Patrick", age=100, country=info.context.headers["country-code"])


schema = strawberry.Schema(query=Query)
