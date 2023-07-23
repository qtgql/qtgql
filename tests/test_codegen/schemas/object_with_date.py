from datetime import date, datetime, timezone

import strawberry

from tests.test_codegen.schemas.node_interface import NODE_DB, Node


@strawberry.type
class User(Node):
    name: str
    age: int
    birth: date


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100, birth=datetime.now(tz=timezone.utc).date())


@strawberry.type
class Mutation:
    @strawberry.field()
    def change_birth(self, node_id: strawberry.ID, new_birth: date) -> User:
        user: User = NODE_DB.get(node_id)
        user.birth = new_birth
        return user


schema = strawberry.Schema(query=Query, mutation=Mutation)
