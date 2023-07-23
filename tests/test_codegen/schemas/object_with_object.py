from __future__ import annotations

import strawberry

from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import NODE_DB, Node


# WARNING: This schema correlates with the optional nested object schema
@strawberry.type
class User(Node):
    person: Person


@strawberry.type()
class Person(Node):
    name: str
    age: int


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return User(person=Person(name=fake.name(), age=fake.pyint()))


@strawberry.type
class Mutation:
    @strawberry.field()
    def change_name(self, node_id: strawberry.ID, new_name: str) -> User:
        user: User = NODE_DB.get(node_id)
        user.person.name = new_name
        return user

    @strawberry.field()
    def replace_person(self, node_id: strawberry.ID) -> User:
        user: User = NODE_DB.get(node_id)
        user.person = Person(name=fake.name(), age=fake.pyint())
        return user


schema = strawberry.Schema(query=Query, mutation=Mutation)
