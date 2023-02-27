import uuid
from uuid import UUID

import strawberry

from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import Node


@strawberry.type
class User(Node):
    name: str
    age: int
    age_point: float
    male: bool
    id: strawberry.ID
    uuid: UUID


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(
            name=fake.name(),
            age=fake.pyint(),
            age_point=fake.pyfloat(),
            male=fake.pybool(),
            id=strawberry.ID(fake.pystr()),
            uuid=uuid.uuid4(),
        )


schema = strawberry.Schema(query=Query)
