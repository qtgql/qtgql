from __future__ import annotations

import strawberry

from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import Node, NODE_DB


@strawberry.type
class User(Node):
    friends: list[Person]


@strawberry.type()
class Person(Node):
    name: str = strawberry.field(default_factory=fake.name)
    age: int = strawberry.field(default_factory=fake.pyint)


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(friends=[Person() for _ in range(5)])


@strawberry.type()
class Mutation:
    @strawberry.mutation()
    def rename_friend_name(self, friend_id: strawberry.ID, name: str) -> Person:
        p: Person = NODE_DB.get(friend_id)
        p.name = name
        return p


schema = strawberry.Schema(query=Query, mutation=Mutation)
