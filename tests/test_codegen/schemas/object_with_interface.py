import strawberry
from tests.test_codegen.schemas.node_interface import NODE_DB, Node


@strawberry.interface
class UserInterface(Node):
    name: str
    age: int


@strawberry.type
class User(UserInterface):
    ...


@strawberry.type
class Query:
    @strawberry.field()
    def node(self, user_id: strawberry.ID) -> Node:
        u: User = NODE_DB.get(user_id)
        return u

    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100)


schema = strawberry.Schema(query=Query)
