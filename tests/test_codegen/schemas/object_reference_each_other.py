from __future__ import annotations

from typing import Optional

import strawberry

from tests.conftest import fake


@strawberry.type
class User:
    password: str
    person: Optional[Person]


@strawberry.type()
class Person:
    name: str = fake.name()
    age: int = fake.pyint()
    user: User


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(password="fake.password", person=Person(user=self))


schema = strawberry.Schema(query=Query)
