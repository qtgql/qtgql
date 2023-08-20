from __future__ import annotations

import strawberry

from ...conftest import factory
from .node_interface import NODE_DB, Node


@strawberry.type()
class UserWithFriend(Node):
    name: str = strawberry.field(default_factory=factory.person.name)

    been_here: strawberry.Private[bool] = False

    @strawberry.field()
    def friend(
        self,
        connected_arg: bool,
    ) -> UserWithFriend | None:
        if not self.been_here:
            self._connected_friend = UserWithFriend()
            self._disconnected_friend = UserWithFriend()
            self.been_here = True
        if connected_arg:
            return self._connected_friend
        return self._disconnected_friend


@strawberry.type()
class Query:
    @strawberry.field()
    def user(self) -> UserWithFriend:
        return UserWithFriend()


@strawberry.type()
class Mutation:
    @strawberry.mutation
    def change_friend_name(
        self,
        connected: bool,
        new_name: str,
        user_id: strawberry.ID,
    ) -> UserWithFriend:
        user: UserWithFriend = NODE_DB.get(user_id)
        friend = user.friend(connected)
        friend.name = new_name
        return user


schema = strawberry.Schema(query=Query, mutation=Mutation)
