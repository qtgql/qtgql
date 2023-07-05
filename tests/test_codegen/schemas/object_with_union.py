from __future__ import annotations

import enum

import strawberry
from tests.conftest import factory
from tests.test_codegen.schemas.node_interface import Node


@strawberry.type()
class Frog:
    name: str = strawberry.field(default_factory=factory.person.name)
    color: str = strawberry.field(default_factory=factory.text.color)


@strawberry.type
class User(Node):
    who_am_i: Frog | Person


@strawberry.enum()
class UnionChoice(enum.Enum):
    PERSON, FROG = range(2)


@strawberry.type()
class Person:
    name: str = strawberry.field(default_factory=factory.person.name)
    age: int = strawberry.field(default_factory=factory.person.age)


@strawberry.type
class Query:
    @strawberry.field
    def user(self, choice: UnionChoice = UnionChoice.PERSON) -> User:
        if choice is UnionChoice.PERSON:
            return User(who_am_i=Person())
        return User(who_am_i=Frog())


schema = strawberry.Schema(query=Query)
