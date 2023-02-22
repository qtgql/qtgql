from typing import Optional

import strawberry

from tests.test_codegen.schemas.node_interface import Node


@strawberry.type
class User(Node):
    name: Optional[str]
    age: Optional[int]


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100)


schema = strawberry.Schema(query=Query)
