import enum
import random

import strawberry
from tests.conftest import factory


@strawberry.enum()
class Gender(enum.Enum):
    MALE, FEMALE = range(2)


@strawberry.enum()
class AnimalKind(enum.Enum):
    PERSON, DOG = range(2)


@strawberry.interface
class AnimalInterface:
    kind: AnimalKind = "Not implemented"
    gender: Gender = strawberry.field(
        default_factory=lambda: random.choice([Gender.MALE, Gender.FEMALE]),  # noqa: S311
    )
    age: int = strawberry.field(default_factory=factory.person.age)


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


schema = strawberry.Schema(query=Query, types=[Person, Dog])
