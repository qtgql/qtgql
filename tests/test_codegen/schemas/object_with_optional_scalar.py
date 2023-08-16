from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
from uuid import UUID

import strawberry

from tests.conftest import factory
from tests.test_codegen.schemas.node_interface import NODE_DB, Node

if TYPE_CHECKING:
    from datetime import datetime


@strawberry.type
class User(Node):
    name: str | None = None
    age: int | None = None
    age_point: float | None = None
    uuid: UUID | None = None
    birth: datetime | None = None


def create_nonnull_user() -> User:
    return User(
        name=factory.person.name(),
        age=factory.person.age(),
        age_point=factory.numeric.float_number(),
        uuid=uuid.uuid4(),
        birth=factory.datetime.datetime(),
    )


@strawberry.type
class Query:
    @strawberry.field
    def user(self, ret_none: bool = False) -> User:
        if ret_none:
            return User()
        return create_nonnull_user()


@strawberry.type()
class Mutation:
    @strawberry.field()
    def fill_user(self, user_id: strawberry.ID) -> User:
        user: User = NODE_DB.get(user_id)
        new_user = create_nonnull_user()
        new_user.id = user.id
        return new_user

    @strawberry.field()
    def nullify_user(self, user_id: strawberry.ID) -> User:
        user: User = NODE_DB.get(user_id)
        nulled_user = User()
        nulled_user.id = user.id
        return nulled_user


schema = strawberry.Schema(query=Query, mutation=Mutation)
