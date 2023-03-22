from __future__ import annotations

import strawberry

from tests.conftest import fake


@strawberry.type
class User:
    name: str
    age: int


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name=fake.name(), age=fake.pyint())


schema = strawberry.Schema(query=Query)
