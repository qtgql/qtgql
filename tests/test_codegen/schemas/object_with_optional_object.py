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
    def user(self, return_null: bool = False) -> User:
        if return_null:
            return User(person=None)
        else:
            return User(person=Person(name="nir", age=24))


schema = strawberry.Schema(query=Query)
