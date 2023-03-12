from __future__ import annotations

import strawberry

from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import Node


@strawberry.type
class User(Node):
    persons: list[Person]


@strawberry.type()
class Person(Node):
    name: str
    age: int


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        persons = [Person(name=fake.name(), age=fake.pyint()) for _ in range(5)]
        return User(persons=persons)

    @strawberry.field()
    def userWithSamePerson(self) -> User:
        user = Query.user(None)
        fp = user.persons[0]
        for person in user.persons:
            person.id = fp.id
        return user


schema = strawberry.Schema(query=Query)
