from __future__ import annotations

import random
from enum import Enum

import strawberry
from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import Node


@strawberry.type
class Person(Node):
    name: str = strawberry.field(default_factory=fake.name)
    age: int = strawberry.field(default_factory=fake.pyint)


@strawberry.type()
class Frog(Node):
    name: str = "Kermit"
    color: str = "green"


UNION_LIST = [random.choice((Person(), Frog())) for _ in range(7)]  # noqa: S311


@strawberry.type
class Query:
    @strawberry.field
    def usersAndFrogs(self) -> list[Frog | Person]:
        return UNION_LIST


@strawberry.enum()
class UnionTypes(Enum):
    PERSON, FROG = range(2)


@strawberry.type()
class Mutation:
    @strawberry.field()
    def insert_to_list(self, at: int, name: str, type: UnionTypes) -> None:
        if type is UnionTypes.PERSON:
            UNION_LIST.insert(at, Person(name=name))
        else:
            UNION_LIST.insert(at, Frog(name=name))

    @strawberry.field()
    def modify_name(self, at: int, name: str) -> None:
        UNION_LIST[at].name = name


schema = strawberry.Schema(query=Query, mutation=Mutation)
