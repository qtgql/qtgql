from __future__ import annotations

import random

import strawberry

from tests.conftest import fake


@strawberry.type()
class Frog:
    name: str = fake.name()
    color: str = "green"


@strawberry.type
class User:
    who_am_i: Frog | Person


@strawberry.type()
class Person:
    name: str = fake.name()
    age: int = fake.pyint()


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return random.choice([User(who_am_i=Person()), User(who_am_i=Frog())])


schema = strawberry.Schema(query=Query)
