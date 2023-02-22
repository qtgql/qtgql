from datetime import datetime, time, timedelta

import strawberry

from tests.test_codegen.schemas.node_interface import Node


@strawberry.type
class User(Node):
    name: str
    age: int
    whatTimeIsIt: time


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(
            name="Patrick", age=100, whatTimeIsIt=(datetime.now() - timedelta(hours=5)).time()
        )


schema = strawberry.Schema(query=Query)
