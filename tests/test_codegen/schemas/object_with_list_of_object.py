from __future__ import annotations

import strawberry

from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import Node


@strawberry.type
class User(Node):
    friends: list[Person]


@strawberry.type()
class Person(Node):
    name: str
    age: int


FRIENDS = [Person(name=fake.name(), age=fake.pyint()) for _ in range(5)]
@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(friends=FRIENDS)





schema = strawberry.Schema(query=Query)
