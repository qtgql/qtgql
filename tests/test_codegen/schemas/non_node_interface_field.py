from __future__ import annotations

import enum
import random
import uuid

import strawberry

from tests.conftest import factory

DB: dict[str, AnimalInterface] = {}


@strawberry.enum()
class Gender(enum.Enum):
    MALE, FEMALE = range(2)


@strawberry.enum()
class AnimalKind(enum.Enum):
    PERSON, DOG = range(2)


@strawberry.interface
class AnimalInterface:
    id: strawberry.ID = strawberry.field(default_factory=lambda: uuid.uuid4().hex)
    kind: AnimalKind = "Not implemented"
    gender: Gender = strawberry.field(
        default_factory=lambda: random.choice([Gender.MALE, Gender.FEMALE]),  # noqa: S311
    )
    age: int = strawberry.field(default_factory=factory.person.age)

    def __post_init__(self) -> None:
        DB[self.id] = self


@strawberry.type
class Dog(AnimalInterface):
    kind: AnimalKind = AnimalKind.DOG
    fur_color: str = strawberry.field(factory.text.color)


@strawberry.type
class Person(AnimalInterface):
    kind: AnimalKind = AnimalKind.PERSON
    language: str = strawberry.field(factory.person.language)


@strawberry.type
class Query:
    @strawberry.field
    def animal(self, kind: AnimalKind) -> AnimalInterface:
        if kind is kind.DOG:
            return Dog()
        return Person()


@strawberry.type()
class Mutation:
    @strawberry.field()
    def change_age(self, animal_id: strawberry.ID, new_age: int) -> AnimalInterface:
        animal = DB[animal_id]
        animal.age = new_age
        return animal


schema = strawberry.Schema(query=Query, mutation=Mutation, types=[Person, Dog])
