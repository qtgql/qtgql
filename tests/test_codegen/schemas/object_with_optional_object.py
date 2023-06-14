from __future__ import annotations

import strawberry
from tests.test_codegen.schemas.node_interface import NODE_DB, Node


@strawberry.type
class User(Node):
    person: Person | None


@strawberry.type()
class Person(Node):
    name: str
    age: int


@strawberry.type
class Query:
    @strawberry.field
    def user(self, return_null: bool = False) -> User:
        if return_null:
            return User(person=None)
        else:
            return User(person=Person(name="nir", age=24))


@strawberry.type
class Mutation:
    @strawberry.field()
    def change_name(self, node_id: strawberry.ID, new_name: str) -> User:
        user: User = NODE_DB.get(node_id)
        user.person.name = new_name
        return user


schema = strawberry.Schema(query=Query, mutation=Mutation)
