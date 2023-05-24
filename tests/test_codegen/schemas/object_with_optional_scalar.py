import uuid
from datetime import datetime
from datetime import timezone
from typing import Optional
from uuid import UUID

import strawberry

from tests.test_codegen.schemas.node_interface import Node


@strawberry.type
class User(Node):
    name: Optional[str] = None
    age: Optional[int] = None
    age_point: Optional[float] = None
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


schema = strawberry.Schema(query=Query)
