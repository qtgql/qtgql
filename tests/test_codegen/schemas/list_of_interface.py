from enum import Enum

import strawberry

from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import Node


@strawberry.interface
class HasNameAgeInterface(Node):
    name: str = strawberry.field(default_factory=fake.name)
    age: int = strawberry.field(default_factory=fake.pyint)


@strawberry.type
class User(HasNameAgeInterface):
    password: str = strawberry.field(default_factory=fake.password)


@strawberry.type
class Dog(HasNameAgeInterface):
    barks: bool = strawberry.field(default_factory=fake.pybool)


@strawberry.enum()
class TypesEnum(Enum):
    Dog = Dog.__name__
    User = User.__name__


@strawberry.type
class Query:
    @strawberry.field
    def node(self, ret: TypesEnum = TypesEnum.Dog) -> list[Node]:
        if ret is TypesEnum.Dog:
            return [Dog() for _ in range(5)]
        else:
            return [User() for _ in range(5)]

    @strawberry.field()
    def dog(self) -> Dog:
        return Dog()

    @strawberry.field()
    def user(self) -> User:
        return User()


schema = strawberry.Schema(query=Query)
