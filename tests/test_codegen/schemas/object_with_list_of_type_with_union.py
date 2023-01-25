from __future__ import annotations

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


@strawberry.type()
class UserManager:
    name: str = fake.name()

    @strawberry.field
    def users(self) -> list[User]:
        return [User(who_am_i=Person()), User(who_am_i=Frog())]


@strawberry.type
class Query:
    @strawberry.field
    def user_manager(self) -> UserManager:
        return UserManager()


schema = strawberry.Schema(query=Query)
