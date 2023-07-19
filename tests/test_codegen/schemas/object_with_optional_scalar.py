from __future__ import annotations

import uuid
from datetime import datetime, timezone
from uuid import UUID

import strawberry

from tests.test_codegen.schemas.node_interface import NODE_DB, Node


@strawberry.type
class User(Node):
    name: str | None = None
    age: int | None = None
    age_point: float | None = None
    uuid: UUID | None = None
    birth: datetime | None = None


@strawberry.type
class Query:
    @strawberry.field
    def user(self, ret_none: bool = False) -> User:
        if ret_none:
            return User()
        return User(
            name="Patrick",
            age=100,
            age_point=100.0,
            uuid=uuid.uuid4(),
            birth=datetime.now(tz=timezone.utc),
        )


@strawberry.type()
class Mutation:
    @strawberry.field()
    def modify_name(self, user_id: strawberry.ID, new_name: str) -> User | None:
        user: User = NODE_DB.get(user_id)
        assert user
        user.name = new_name
        return user


schema = strawberry.Schema(query=Query, mutation=Mutation)
