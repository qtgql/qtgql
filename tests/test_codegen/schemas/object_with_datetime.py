from datetime import datetime

import strawberry


@strawberry.type
class User:
    name: str
    age: int
    birth: datetime


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100, birth=datetime.now())


schema = strawberry.Schema(query=Query)
