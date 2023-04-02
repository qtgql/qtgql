from datetime import date
from datetime import timezone

import strawberry

from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import Node


@strawberry.type
class User(Node):
    name: str
    age: int
    birth: date


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100, birth=fake.date_of_birth(tzinfo=timezone.utc))


schema = strawberry.Schema(query=Query)
