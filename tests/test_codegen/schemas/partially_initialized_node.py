from __future__ import annotations

import uuid
from datetime import datetime  # noqa
from uuid import UUID

import strawberry

from tests.conftest import factory
from tests.test_codegen.schemas.node_interface import NODE_DB, Node


@strawberry.type
class User(Node):
    name: str
    age: int
    age_point: float
    uuid: UUID
    birth: datetime

    @classmethod
    def create(cls) -> User:
        return User(
            name=factory.person.name(),
            age=factory.person.age(),
            age_point=factory.numeric.float_number(),
            uuid=uuid.uuid4(),
            birth=factory.datetime.datetime(),
        )


@strawberry.type
class Query:
    @strawberry.field()
    def create_user(self) -> User:
        return User.create()

    @strawberry.field()
    def get_user_by_id(self, user_id: strawberry.ID) -> User:
        return NODE_DB.get(user_id)


schema = strawberry.Schema(query=Query)
