from typing import Optional

import strawberry


@strawberry.type
class User:
    name: Optional[str]
    age: Optional[int]


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100)


schema = strawberry.Schema(query=Query)
