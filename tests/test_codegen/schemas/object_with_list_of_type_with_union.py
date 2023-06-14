from __future__ import annotations

import strawberry
from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import Node


@strawberry.type()
class Frog(Node):
    name: str = fake.name()
    color: str = "green"


@strawberry.type
class User(Node):
    who_am_i: Frog | Person


@strawberry.type()
class Person(Node):
    name: str = fake.name()
    age: int = fake.pyint()


@strawberry.type()
class UserManager(Node):
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
