from __future__ import annotations

import strawberry

from ...conftest import factory
from .node_interface import Node

friends: dict[UserWithFriend : tuple[UserWithFriend, UserWithFriend]] = {}


def get_or_create_friends(inst: UserWithFriend) -> UserWithFriend:
    ret = friends.get(inst)
    if not ret:
        ret = (UserWithFriend(), UserWithFriend())
        friends[inst] = ret
    return ret


@strawberry.input()
class ConnectedInput:
    bool_var: bool


@strawberry.type()
class UserWithFriend(Node):
    name: str = strawberry.field(default_factory=factory.person.name)

    @strawberry.field()
    def friend(
        self,
        connected_arg: ConnectedInput,
    ) -> UserWithFriend | None:
        friends_ = get_or_create_friends(self)
        if connected_arg:
            return friends_[0]

        return UserWithFriend()


CONST_USER = UserWithFriend()


@strawberry.type()
class Query:
    @strawberry.field()
    def user(self, foo: int = 0) -> UserWithFriend:
        return CONST_USER


schema = strawberry.Schema(query=Query)
