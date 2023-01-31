from datetime import datetime, time

import strawberry


@strawberry.type
class User:
    name: str
    age: int
    whatTimeIsIt: time


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100, whatTimeIsIt=datetime.now().time())


schema = strawberry.Schema(query=Query)
