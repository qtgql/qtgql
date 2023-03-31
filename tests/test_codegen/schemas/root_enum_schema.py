from enum import auto
from enum import Enum

import strawberry


@strawberry.enum
class Status(Enum):
    Connected = auto()
    Stale = auto()
    Disconnected = auto()


@strawberry.type
class Query:
    @strawberry.field
    def status(self) -> Status:
        return Status.Connected


schema = strawberry.Schema(query=Query)

if __name__ == "__main__":
    ...
