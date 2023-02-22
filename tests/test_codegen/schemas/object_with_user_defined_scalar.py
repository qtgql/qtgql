import strawberry

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
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100, country="isr")


schema = strawberry.Schema(query=Query)
