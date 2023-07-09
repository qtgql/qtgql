from __future__ import annotations

import random
from enum import Enum

import strawberry
from tests.conftest import factory, fake
from tests.test_codegen.schemas.node_interface import NODE_DB, Node


@strawberry.type
class Dog(Node):
    name: str = strawberry.field(default_factory=fake.name)
    age: int = strawberry.field(default_factory=fake.pyint)


@strawberry.type()
class Cat:
    name: str = strawberry.field(default_factory=fake.name)
    color: str = strawberry.field(default_factory=factory.text.color)


@strawberry.type()
class Person(Node):
    pets: list[Cat | Dog]
    name: str = strawberry.field(default_factory=fake.name)

    @classmethod
    def create(cls):
        return Person(
            pets=[random.choice((Dog(), Cat())) for _ in range(7)],  # noqa: S311
        )


@strawberry.type
class Query:
    @strawberry.field
    def randPerson(self) -> Person:
        return Person.create()


@strawberry.enum()
class UnionTypes(Enum):
    PERSON, DOG = range(2)


@strawberry.type()
class Mutation:
    @strawberry.field()
    def insert_to_list(
        self,
        node_id: strawberry.ID,
        at: int,
        name: str,
        type: UnionTypes,
    ) -> Person:
        p: Person = NODE_DB.get(node_id)
        if type is UnionTypes.PERSON:
            p.pets.insert(at, Cat(name=name))
        else:
            p.pets.insert(at, Dog(name=name))
        return p

    @strawberry.field()
    def modify_name(self, node_id: strawberry.ID, at: int, name: str) -> Person:
        p: Person = NODE_DB.get(node_id)
        p.pets[at].name = name
        return p

    @strawberry.field()
    def remove_at(self, node_id: strawberry.ID, at: int) -> Person:
        p: Person = NODE_DB.get(node_id)
        p.pets.pop(at)
        return p


schema = strawberry.Schema(query=Query, mutation=Mutation)
