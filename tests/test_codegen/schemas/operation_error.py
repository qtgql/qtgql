import strawberry
from tests.test_codegen.schemas.node_interface import Node


@strawberry.type
class User(Node):
    name: str
    age: int


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        raise Exception({"error": "fdsaafdsaf"})


schema = strawberry.Schema(query=Query)
