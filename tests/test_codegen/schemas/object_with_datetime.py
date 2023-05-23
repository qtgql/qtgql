from datetime import datetime
from datetime import timezone

import strawberry

from tests.test_codegen.schemas.node_interface import Node


@strawberry.type
class User(Node):
    name: str
    age: int
    birth: datetime


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100, birth=datetime.now(tz=timezone.utc))


schema = strawberry.Schema(query=Query)
