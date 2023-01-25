import strawberry


@strawberry.interface
class UserInterface:
    name: str
    age: str


@strawberry.type
class User(UserInterface):
    ...


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(name="Patrick", age=100)


schema = strawberry.Schema(query=Query)
