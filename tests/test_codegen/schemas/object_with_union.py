from __future__ import annotations

import enum
from typing import Union

import strawberry

from tests.test_codegen.schemas.node_interface import Node


@strawberry.type()
class Frog(Node):
    name: str = "Kermit"
    color: str = "green"


@strawberry.type
class User(Node):
    who_am_i: Union[Frog, Person]


@strawberry.enum()
class UnionChoice(enum.Enum):
    PERSON, FROG = range(2)


@strawberry.type()
class Person(Node):
    name: str = "Nir"
    age: int = 24


@strawberry.type
class Query:
    @strawberry.field
    def user(self, choice: UnionChoice = UnionChoice.PERSON) -> User:
        if choice is UnionChoice.PERSON:
            return User(who_am_i=Person())
        return User(who_am_i=Frog())


schema = strawberry.Schema(query=Query)
