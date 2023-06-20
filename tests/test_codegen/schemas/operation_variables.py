from __future__ import annotations

import strawberry

from ...conftest import factory
from .node_interface import Node

friends: dict[UserWithFriend : tuple[UserWithFriend, UserWithFriend]] = {}


@strawberry.type()
class UserWithFriend(Node):
    name: str = strawberry.field(default_factory=factory.person.name)

    @strawberry.field()
    def friend(
        self,
        connected_arg: bool,
    ) -> UserWithFriend | None:
        if connected_arg:
            return CONNECTED_FRIEND
        return DISCONNECTED_FRIENDS


CONST_USER = UserWithFriend()
CONNECTED_FRIEND = UserWithFriend()
DISCONNECTED_FRIENDS = UserWithFriend()


@strawberry.type()
class Query:
    @strawberry.field()
    def user(self, foo: int = 0) -> UserWithFriend:
        return CONST_USER


@strawberry.type()
class Mutation:
    @strawberry.mutation
    def change_friend_name(self, connected: bool, new_name: str) -> UserWithFriend:
        f = CONST_USER.friend(connected)
        f.name = new_name
        return CONST_USER


schema = strawberry.Schema(query=Query, mutation=Mutation)
