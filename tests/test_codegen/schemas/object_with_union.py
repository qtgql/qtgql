from __future__ import annotations

import random
from typing import Union

import strawberry

from tests.test_codegen.schemas.node_interface import Node


@strawberry.type()
class Frog(Node):
    name: str = "Kermit"
    color: str = "green"


@strawberry.type
class User(Node):
    who_am_i: Union[Frog, Person]


@strawberry.type()
class Person(Node):
    name: str = "Nir"
    age: int = 24


@strawberry.type
class Query:
    @strawberry.field
    def user(self) -> User:
        return random.choice([User(who_am_i=Person()), User(who_am_i=Frog())])


schema = strawberry.Schema(query=Query)
