from __future__ import annotations

from typing import Optional

import strawberry

from tests.conftest import fake


@strawberry.type
class User:
    id: Optional[strawberry.ID]
    name: str
    age: int


@strawberry.type
class Query:
    @strawberry.field
    def users(self) -> list[User]:
        return [User(name=fake.name(), age=fake.pyint()) for _ in range(4)]


schema = strawberry.Schema(query=Query)
