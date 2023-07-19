from enum import Enum, auto

import strawberry

from tests.test_codegen.schemas.node_interface import NODE_DB, Node


@strawberry.enum
class Status(Enum):
    Connected = auto()
    Stale = auto()
    Disconnected = auto()


@strawberry.type
class User(Node):
    name: str
    age: int
    status: Status = Status.Connected


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100)


@strawberry.type()
class Mutation:
    @strawberry.field()
    def update_status(self, user_id: strawberry.ID, status: Status) -> User:
        u: User = NODE_DB.get(user_id)
        u.status = status
        return u


schema = strawberry.Schema(query=Query, mutation=Mutation)

if __name__ == "__main__":
    ...
