from __future__ import annotations

import strawberry

from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import Node


# WARNING: This schema correlates with the optional nested object schema
@strawberry.type
class User(Node):
    person: Person


@strawberry.type()
class Person(Node):
    name: str
    age: int


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(person=Person(name=fake.name(), age=fake.pyint()))


schema = strawberry.Schema(query=Query)
