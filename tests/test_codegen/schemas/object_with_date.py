from datetime import date

import strawberry


@strawberry.type
class User:
    name: str
    age: int
    birth: date


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100, birth=date.today())


schema = strawberry.Schema(query=Query)
