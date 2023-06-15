from decimal import Decimal

import strawberry
from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import NODE_DB, Node


@strawberry.type
class User(Node):
    name: str
    age: int
    balance: Decimal


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100, balance=Decimal(fake.pyfloat()))


@strawberry.type
class Mutation:
    @strawberry.field()
    def change_balance(self, node_id: strawberry.ID, new_balance: Decimal) -> User:
        user: User = NODE_DB.get(node_id)
        user.balance = new_balance
        return user


schema = strawberry.Schema(query=Query, mutation=Mutation)
