from datetime import datetime, timezone

import strawberry

from tests.test_codegen.schemas.node_interface import NODE_DB, Node


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


@strawberry.type
class Mutation:
    @strawberry.field()
    def change_birth(self, node_id: strawberry.ID, new_birth: datetime) -> User:
        user: User = NODE_DB.get(node_id)
        user.birth = new_birth
        return user


schema = strawberry.Schema(query=Query, mutation=Mutation)
