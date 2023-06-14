from datetime import datetime, time, timezone

import strawberry
from tests.test_codegen.schemas.node_interface import NODE_DB, Node


@strawberry.type
class User(Node):
    name: str
    age: int
    lunch_time: time


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100, lunch_time=datetime.now(tz=timezone.utc).time())


@strawberry.type
class Mutation:
    @strawberry.field()
    def change_lunch_time(self, node_id: strawberry.ID, new_time: time) -> User:
        user: User = NODE_DB.get(node_id)
        user.lunch_time = new_time
        return user


schema = strawberry.Schema(query=Query, mutation=Mutation)
