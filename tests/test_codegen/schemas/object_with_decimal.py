from decimal import Decimal

import strawberry


@strawberry.type
class User:
    name: str
    age: int
    balance: Decimal


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100, balance=Decimal(10000000.0))


schema = strawberry.Schema(query=Query)
