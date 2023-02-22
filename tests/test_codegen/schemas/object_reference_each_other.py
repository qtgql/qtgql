from __future__ import annotations

from typing import Optional

import strawberry

from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import Node


@strawberry.type
class User(Node):
    password: str
    person: Optional[Person]


@strawberry.type()
class Person(Node):
    name: str = fake.name()
    age: int = fake.pyint()
    user: User


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(password="fake.password", person=Person(user=self))


schema = strawberry.Schema(query=Query)
