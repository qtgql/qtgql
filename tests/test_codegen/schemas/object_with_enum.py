from enum import Enum, auto

import strawberry


@strawberry.enum
class Status(Enum):
    Connected = auto()
    Stale = auto()
    Disconnected = auto()


@strawberry.type
class User:
    name: str
    age: int
    status: Status = Status.Connected


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100)


schema = strawberry.Schema(query=Query)

if __name__ == "__main__":
    ...
