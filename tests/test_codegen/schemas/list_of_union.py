from __future__ import annotations

import random
import uuid
from typing import Union
from uuid import UUID

import strawberry

from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import Node


@strawberry.type
class User(Node):
    name: str = strawberry.field(default_factory=fake.name)
    age: int = strawberry.field(default_factory=fake.pyint)
    age_point: float = strawberry.field(default_factory=fake.pyfloat)
    male: bool = strawberry.field(default_factory=fake.pybool)
    id: strawberry.ID = strawberry.field(default_factory=lambda: strawberry.ID(fake.pystr()))
    uuid: UUID = strawberry.field(default_factory=uuid.uuid4)


@strawberry.type()
class Frog(Node):
    name: str = "Kermit"
    color: str = "green"


@strawberry.type
class Query:
    @strawberry.field
    def usersAndFrogs(self) -> list[Union[Frog, User]]:
        return [random.choice((User(), Frog())) for _ in range(7)]  # noqa: S311


schema = strawberry.Schema(query=Query)
