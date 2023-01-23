from __future__ import annotations

import strawberry


@strawberry.type
class User:
    person: Person


@strawberry.type()
class Person:
    name: str
    age: int


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(person=Person(name="Patrick", age=100))


schema = strawberry.Schema(query=Query)
