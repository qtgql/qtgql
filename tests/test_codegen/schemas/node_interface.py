import uuid

import strawberry


@strawberry.interface
class Node:
    id: strawberry.ID = strawberry.field(default_factory=lambda: uuid.uuid4().hex)
