from __future__ import annotations

import strawberry

from tests.conftest import fake


@strawberry.type
class User:
    persons: list[Person]


@strawberry.type()
class Person:
    name: str
    age: int


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(persons=[Person(name=fake.name(), age=fake.pyint())])


schema = strawberry.Schema(query=Query)
