from __future__ import annotations

import uuid
from uuid import UUID

import strawberry

from tests.conftest import factory
from tests.test_codegen.schemas.node_interface import Node


@strawberry.type
class User(Node):
    name: str = strawberry.field(default_factory=factory.person.name)
    age: int = strawberry.field(default_factory=factory.person.age)
    age_point: float = strawberry.field(default_factory=factory.numeric.float_number)
    male: bool = strawberry.field(default_factory=factory.develop.boolean)
    id: strawberry.ID = strawberry.field(default_factory=lambda: strawberry.ID(uuid.uuid4().hex))
    uuid: UUID = strawberry.field(default_factory=uuid.uuid4)


CONST_USER = User(
    name="nir",
    age=24,
    age_point=24.0,
    male=True,
    id="FakeID",
    uuid=UUID("06335e84-2872-4914-8c5d-3ed07d2a2f16"),
)


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User()

    @strawberry.field()
    def constUser(self) -> User:
        return CONST_USER


@strawberry.type()
class Mutation:
    @strawberry.field(description="randomizes the current const user")
    def randomize_const_user(self) -> User:
        new_user = User()
        CONST_USER.name = new_user.name
        CONST_USER.age = new_user.age
        CONST_USER.male = new_user.male


schema = strawberry.Schema(query=Query, mutation=Mutation)
