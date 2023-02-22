from __future__ import annotations

from typing import Optional

import strawberry

from tests.test_codegen.schemas.node_interface import Node


@strawberry.type
class User(Node):
    person: Optional[Person]


@strawberry.type()
class Person(Node):
    name: str
    age: int


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(person=None)


schema = strawberry.Schema(query=Query)
