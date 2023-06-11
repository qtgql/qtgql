from __future__ import annotations

import strawberry

from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import Node, NODE_DB


@strawberry.type
class User(Node):
    friends: list[Person]


@strawberry.type()
class Person(Node):
    name: str = strawberry.field(default_factory=fake.name())
    age: int = strawberry.field(default_factory=fake.pyint())


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(friends=[Person() for _ in range(5)])


@strawberry.type()
class Mutation:
    @strawberry.mutation()
    def add_friend(self, user_id: strawberry.ID) -> User:
        user: User = NODE_DB.get_node(user_id)
        user.friends.append(Person())
        return user


schema = strawberry.Schema(query=Query)
