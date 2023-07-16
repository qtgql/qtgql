from __future__ import annotations

import enum

import strawberry
from tests.conftest import factory
from tests.test_codegen.schemas.node_interface import Node


@strawberry.type()
class Frog(Node):
    name: str = strawberry.field(default_factory=factory.person.name)
    color: str = strawberry.field(default_factory=factory.text.color)


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
    def who_am_i(self, choice: UnionChoice = UnionChoice.PERSON) -> Frog | Person:
        if choice is UnionChoice.PERSON:
            return Person()
        return Frog()


schema = strawberry.Schema(query=Query)
