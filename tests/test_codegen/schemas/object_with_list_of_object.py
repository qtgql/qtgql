from __future__ import annotations

import strawberry
from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import NODE_DB, Node

user_friends: dict[User, list[Person]] = {}


@strawberry.type
class User(Node):
    @strawberry.field()
    def friends(self) -> list[Person]:
        if ret := user_friends.get(self, None):
            return ret

        user_friends[self] = ret = [Person() for _ in range(20)]
        return ret


@strawberry.type()
class Person(Node):
    name: str = strawberry.field(default_factory=fake.name)
    age: int = strawberry.field(default_factory=fake.pyint)


@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: strawberry.ID | None = None) -> User:
        return User()


@strawberry.type()
class Mutation:
    @strawberry.mutation()
    def add_friend(self, user_id: strawberry.ID, name: str) -> None:
        u: User = NODE_DB.get(user_id)
        u.friends.append(Person(name=name))


schema = strawberry.Schema(query=Query, mutation=Mutation)
