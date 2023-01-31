from datetime import datetime
from enum import Enum

import strawberry


@strawberry.enum
class Status(Enum):
    Connected, Stale, Disconnected = range(3)


@strawberry.type
class User:
    name: str
    age: int
    status: Status = Status.Connected


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100, birth=datetime.now())


schema = strawberry.Schema(query=Query)

if __name__ == "__main__":
    ...
