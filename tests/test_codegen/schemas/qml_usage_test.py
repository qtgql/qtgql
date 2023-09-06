"""No new features are tested here.

only qml usages of existing features.
"""
from __future__ import annotations

import strawberry

from tests.conftest import fake
from tests.test_codegen.schemas.node_interface import Node

store: dict[str, dict[str, Friend]] = {}


@strawberry.type
class Friend(Node):
    name: str
    age: int


@strawberry.type
class Query:
    @strawberry.field()
    def simple_field(self) -> bool:
        return True

    @strawberry.field
    def friends(self, store_id: str) -> list[Friend]:
        if friends := store.get(store_id, None):
            return list(friends.values())

        ret = [Friend(name=fake.name(), age=fake.pyint()) for _ in range(4)]

        store[store_id] = {u.id: u for u in ret}
        return ret


def remove_friend_impl(store_id: str, friend_id: strawberry.ID) -> None:
    friends = store.get(store_id)
    friends.pop(friend_id)


@strawberry.type()
class Mutation:
    @strawberry.mutation
    def remove_friend(self, store_id: str, friend_id: strawberry.ID) -> bool:
        remove_friend_impl(store_id, friend_id)
        return True

    @strawberry.field()
    def remove_friends(self, store_id: str, friends: list[strawberry.ID]) -> None:
        for friend in friends:
            remove_friend_impl(store_id, friend)


schema = strawberry.Schema(query=Query, mutation=Mutation)
