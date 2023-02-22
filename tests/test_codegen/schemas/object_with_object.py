from __future__ import annotations

import strawberry

from tests.test_codegen.schemas.node_interface import Node


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
        return User(person=Person(name="Patrick", age=100))


schema = strawberry.Schema(query=Query)
