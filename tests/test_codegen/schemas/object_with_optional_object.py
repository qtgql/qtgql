from __future__ import annotations

from typing import Optional

import strawberry


@strawberry.type
class User:
    person: Optional[Person]


@strawberry.type()
class Person:
    name: str
    age: int


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(person=None)


schema = strawberry.Schema(query=Query)
