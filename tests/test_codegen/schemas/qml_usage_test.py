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


@strawberry.type()
class Mutation:
    @strawberry.mutation
    def remove_friend(self, store_id: str, friend_id: strawberry.ID) -> bool:
        friends = store.get(store_id)
        friends.pop(friend_id)
        return True


schema = strawberry.Schema(query=Query, mutation=Mutation)
