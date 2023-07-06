from __future__ import annotations

import strawberry
from tests.conftest import factory


@strawberry.type
class User:
    name: str = strawberry.field(default_factory=factory.person.name)
    age: int = strawberry.field(default_factory=factory.person.age)


USERS = [User() for _ in range(4)]


@strawberry.type()
class Mutation:
    @strawberry.field()
    def insert_user(self, name: str, at: int) -> None:
        USERS.insert(at, User(name=name))

    @strawberry.field()
    def modify_user(self, at: int, name: str) -> None:
        USERS[at].name = name


@strawberry.type
class Query:
    @strawberry.field
    def users(self) -> list[User]:
        return USERS


schema = strawberry.Schema(query=Query, mutation=Mutation)
