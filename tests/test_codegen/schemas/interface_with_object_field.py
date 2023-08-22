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


@strawberry.type()
class AnimalMetadata:
    kind: AnimalKind = "Not implemented"
    gender: Gender = strawberry.field(
        default_factory=lambda: random.choice([Gender.MALE, Gender.FEMALE]),  # noqa: S311
    )
    age: int = strawberry.field(default_factory=factory.person.age)


@strawberry.interface
class AnimalInterface:
    id: strawberry.ID = strawberry.field(default_factory=lambda: uuid.uuid4().hex)
    metadata: AnimalMetadata = strawberry.field(default_factory=AnimalMetadata)

    def __post_init__(self) -> None:
        DB[self.id] = self


@strawberry.type
class Dog(AnimalInterface):
    fur_color: str

    @classmethod
    def create(cls) -> Dog:
        md = AnimalMetadata()
        md.kind = AnimalKind.DOG
        return Dog(
            fur_color=factory.text.color(),
            metadata=md,
        )


@strawberry.type
class Person(AnimalInterface):
    language: str

    @classmethod
    def create(cls) -> Person:
        md = AnimalMetadata()
        md.kind = AnimalKind.PERSON
        return Person(
            language=factory.person.language(),
            metadata=md,
        )


@strawberry.type
class Query:
    @strawberry.field
    def animal(self, kind: AnimalKind) -> AnimalInterface:
        if kind is kind.DOG:
            return Dog.create()
        return Person.create()


schema = strawberry.Schema(query=Query, types=[Person, Dog])
